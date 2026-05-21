"""
    .. module:: vpncoordinatorcoupling
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the :class:`VPNCoordinatorCoupling`
                   class, the landscape-side coupling that wires a VPN
                   control plane and (optionally) a local VPN daemon
                   into the multi-plane address records on
                   :class:`LandscapeDevice`.

    The coupling is opt-in. A landscape with no ``vpn:`` block in its
    configuration never instantiates it, preserving bit-identical
    backward compatibility with pre-VPN landscapes.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import logging
import os

from typing import Any, Dict, List, Optional

from automojo.aspects.aspects import Aspects
from automojo.errors.exceptions import ConfigurationError
from automojo.interfaces.ivpnclient import IVPNClient
from automojo.interfaces.ivpncontrolplane import IVPNControlPlane, VPNDeviceRecord

from automojo.landscaping.coupling.aspectslandscapecoupling import (
    AspectsLandscapeCoupling,
    DEFAULT_LANDSCAPE_COUPLING_ASPECTS,
)
from automojo.landscaping.coupling.exceptions import (
    VPNCoordinatorAmbiguousMatchError,
)
from automojo.landscaping.coupling.vpncouplingresult import VPNCouplingResult


logger = logging.getLogger(__name__)


# The configuration-block key that selects this coupling kind. A
# landscape whose configuration carries a top-level ``vpn:`` block
# resolves to this kind through the landscape coordinator factory.
VPN_COORDINATOR_COUPLING_KIND = "vpn"

# Module-level registry of landscape coupling kinds. The landscape
# coordinator factory consults this table to map a configuration-block
# key (for example ``"vpn"``) to the coupling class that services it.
_COUPLING_KIND_REGISTRY: Dict[str, type] = {}


def register_coupling_kind(*, kind: str, coupling_type: type) -> None:
    """
        Registers a landscape coupling kind with the landscape
        coordinator factory registry.

        :param kind: The configuration-block key that selects the
            coupling (for example ``"vpn"``).
        :param coupling_type: The coupling class to instantiate when a
            landscape declares the ``kind`` configuration block.
    """
    _COUPLING_KIND_REGISTRY[kind] = coupling_type
    return


def coupling_type_for_kind(*, kind: str) -> type:
    """
        Returns the coupling class registered for ``kind``.

        :param kind: The configuration-block key to look up.

        :returns: The registered coupling class.
        :raises: :class:`ConfigurationError` when ``kind`` has not been
            registered.
    """
    if kind not in _COUPLING_KIND_REGISTRY:
        err_msg_lines = ["No landscape coupling kind registered for the requested key."]
        err_msg_lines.append("KIND: {}".format(kind))
        err_msg_lines.append("REGISTERED KINDS:")
        for registered in _COUPLING_KIND_REGISTRY.keys():
            err_msg_lines.append("    {}".format(registered))
        err_msg = os.linesep.join(err_msg_lines)
        raise ConfigurationError(err_msg)

    rtnval = _COUPLING_KIND_REGISTRY[kind]
    return rtnval


def is_coupling_kind_registered(*, kind: str) -> bool:
    """
        Indicates whether a coupling kind has been registered with the
        landscape coordinator factory registry.

        :param kind: The configuration-block key to test.

        :returns: ``True`` when ``kind`` is registered.
    """
    rtnval = kind in _COUPLING_KIND_REGISTRY
    return rtnval


class VPNCoordinatorCoupling:
    """
        Landscape-side coupling that wires a mesh-VPN control plane into
        the landscape's device records.

        The coupling discovers peer devices via
        :meth:`IVPNControlPlane.list_devices`, matches each peer against
        the configured landscape devices by hostname or tag, and
        populates the matched device's overlay slot via
        :meth:`DeviceAddressSet.set_overlay`.

        When the landscape declares a host as ``vpn.managed=True``, a
        local :class:`IVPNClient` is constructed and registered on the
        device so subsequent landscape operations may drive the local
        daemon.

        The coupling is idempotent: a second :meth:`couple` against the
        same control-plane state produces no further mutations.
    """

    def __init__(self, *, provider: str,
                 control_plane: IVPNControlPlane,
                 vpn_client_factory: Optional[Any] = None,
                 vpn_managed: bool = False) -> None:
        """
            Constructs a new :class:`VPNCoordinatorCoupling`.

            :param provider: Provider identifier (for example
                ``"tailscale"`` or ``"twingate"``). The provider name is
                used as the key into the device's overlay-provider map.
            :param control_plane: The :class:`IVPNControlPlane`
                implementation used to enumerate peer device records.
            :param vpn_client_factory: Optional callable invoked when a
                device declares ``vpn.managed=True``. The callable is
                invoked as ``factory(device=device, provider=provider)``
                and must return an :class:`IVPNClient` (or ``None`` to
                indicate no client could be constructed, which raises
                :class:`ConfigurationError`).
            :param vpn_managed: Default ``vpn.managed`` value applied to
                devices whose configuration does not declare one.
        """
        self._provider: str = provider
        self._control_plane: IVPNControlPlane = control_plane
        self._vpn_client_factory: Optional[Any] = vpn_client_factory
        self._vpn_managed_default: bool = vpn_managed
        return

    @classmethod
    def register(cls) -> None:
        """
            Registers :class:`VPNCoordinatorCoupling` with the landscape
            coordinator factory registry under the ``vpn`` coupling
            kind.

            Once registered, a landscape whose configuration carries a
            top-level ``vpn:`` block resolves to this coupling class
            through the normal factory path.
        """
        register_coupling_kind(kind=VPN_COORDINATOR_COUPLING_KIND,
                               coupling_type=cls)
        return

    @property
    def provider(self) -> str:
        """
            The provider identifier this coupling acts under.

            :returns: The provider name passed at construction.
        """
        rtnval = self._provider
        return rtnval

    @staticmethod
    def _normalise_hostname(value: Optional[str]) -> Optional[str]:
        """
            Lower-case a hostname so the matching index is
            case-insensitive.

            :param value: The hostname to normalise.

            :returns: ``value.lower()`` when ``value`` is a non-empty
                string, otherwise ``None``.
        """
        rtnval: Optional[str] = None
        if value is not None and len(value) > 0:
            rtnval = value.lower()
        return rtnval

    @staticmethod
    def _device_hostname(device: Any) -> Optional[str]:
        """
            Extract a hostname-like identifier from a landscape device.

            Looks for ``hostname`` first, falling back to the legacy
            ``_host`` attribute carried by :class:`LandscapeDevice`.

            :param device: The landscape device.

            :returns: A hostname string, or ``None`` when the device
                exposes no hostname-like attribute.
        """
        rtnval: Optional[str] = None
        candidate = getattr(device, "hostname", None)
        if candidate is not None:
            rtnval = candidate
        else:
            legacy = getattr(device, "_host", None)
            if legacy is not None:
                rtnval = legacy
        return rtnval

    @staticmethod
    def _device_tags(device: Any) -> List[str]:
        """
            Extract the tag list from a landscape device.

            Looks for ``tags`` first (modern surface), falling back to
            the ``FEATURE_TAGS`` class attribute for compatibility with
            today's :class:`LandscapeDevice`.

            :param device: The landscape device.

            :returns: A list of tag strings; empty when the device
                exposes no tag-like attribute.
        """
        rtnval: List[str] = []
        candidate = getattr(device, "tags", None)
        if candidate is not None:
            rtnval = list(candidate)
        else:
            legacy = getattr(device, "FEATURE_TAGS", None)
            if legacy is not None:
                rtnval = list(legacy)
        return rtnval

    @staticmethod
    def _device_managed(device: Any, *, default: bool) -> bool:
        """
            Look up the ``vpn.managed`` flag on a device.

            :param device: The landscape device.
            :param default: The value to return when the device exposes
                no explicit ``vpn.managed`` flag.

            :returns: ``True`` when the device is landscape-managed for
                VPN bring-up, otherwise ``False``.
        """
        rtnval: bool = default
        config = getattr(device, "device_config", None)
        if config is not None:
            vpn_block = config.get("vpn", None)
            if vpn_block is not None and "managed" in vpn_block:
                rtnval = bool(vpn_block["managed"])
        return rtnval

    @staticmethod
    def _device_identifier(device: Any) -> str:
        """
            Return a short identifier suitable for error / log messages.

            :param device: The landscape device.

            :returns: ``device.full_identifier`` when present, else
                ``device.hostname``, else ``repr(device)``.
        """
        rtnval: str = ""
        full = getattr(device, "full_identifier", None)
        if full is not None:
            rtnval = str(full)
        else:
            host = VPNCoordinatorCoupling._device_hostname(device)
            if host is not None:
                rtnval = host
            else:
                rtnval = repr(device)
        return rtnval

    def _aspects_for_control_plane(self,
                                   aspects: AspectsLandscapeCoupling) -> Aspects:
        """
            Translate a :class:`AspectsLandscapeCoupling` into an
            :class:`Aspects` carrier suitable for passing into the
            control-plane API.

            :param aspects: The landscape-level aspects.

            :returns: A new :class:`Aspects` instance whose timeouts
                reflect ``aspects.timeout_seconds``.
        """
        rtnval = Aspects(completion_timeout=aspects.timeout_seconds,
                         connection_timeout=aspects.timeout_seconds)
        return rtnval

    def _build_index(self,
                     records: List[VPNDeviceRecord]) -> Dict[str, VPNDeviceRecord]:
        """
            Build a normalised-hostname index over a list of control
            plane records.

            :param records: The records returned by
                :meth:`IVPNControlPlane.list_devices`.

            :returns: A mapping of ``lower(hostname) -> VPNDeviceRecord``.
                Records whose hostname normalises to ``None`` are not
                indexed.
        """
        rtnval: Dict[str, VPNDeviceRecord] = {}
        for record in records:
            key = self._normalise_hostname(record.hostname)
            if key is not None:
                rtnval[key] = record
        return rtnval

    def _records_matching_tag(self,
                              tag: str,
                              records: List[VPNDeviceRecord]) -> List[VPNDeviceRecord]:
        """
            Return every control-plane record carrying ``tag``.

            :param tag: The landscape-side tag.
            :param records: The list of control-plane records.

            :returns: A list of matching records (possibly empty).
        """
        rtnval: List[VPNDeviceRecord] = []
        for record in records:
            if tag in record.tags:
                rtnval.append(record)
        return rtnval

    def _records_matching_any_tag(self,
                                  tags: List[str],
                                  records: List[VPNDeviceRecord]) -> List[VPNDeviceRecord]:
        """
            Return every control-plane record carrying any tag in
            ``tags``. The returned list is de-duplicated by
            ``device_id``.

            :param tags: The landscape device's tag list.
            :param records: The list of control-plane records.

            :returns: A list of matching records, de-duplicated.
        """
        seen: Dict[str, VPNDeviceRecord] = {}
        for tag in tags:
            matches = self._records_matching_tag(tag, records)
            for match in matches:
                if match.device_id not in seen:
                    seen[match.device_id] = match
        rtnval = list(seen.values())
        return rtnval

    def _apply_overlay(self, *, device: Any,
                       address: Optional[str]) -> bool:
        """
            Apply ``address`` to the device's overlay slot for the
            coupling's provider, but only when the existing value
            differs.

            :param device: The landscape device to mutate.
            :param address: The address to set.

            :returns: ``True`` when the overlay slot was mutated,
                ``False`` when the existing value already matched.
        """
        rtnval: bool = False
        address_set = device.addresses
        existing = address_set.overlay(provider=self._provider)
        if existing != address:
            address_set.set_overlay(provider=self._provider, address=address)
            rtnval = True
        return rtnval

    def _has_registered_vpn_client(self, *, device: Any) -> bool:
        """
            Report whether ``device`` already carries a registered
            :class:`IVPNClient` for this coupling's provider.

            This supports the idempotent contract of :meth:`couple`: a
            second invocation MUST NOT rebuild and re-register a client
            that is already present.

            :param device: The landscape device to inspect.

            :returns: ``True`` when a client for the provider is already
                registered on the device.
        """
        registry = getattr(device, "_vpn_clients", None)
        if registry is None:
            rtnval = False
            return rtnval

        rtnval = self._provider in registry
        return rtnval

    def _register_vpn_client(self, *, device: Any) -> None:
        """
            Construct and register a managed-host :class:`IVPNClient`
            on ``device`` when the coupling is configured with a
            factory.

            :param device: The landscape device to register against.

            :raises: :class:`ConfigurationError` when no factory is
                configured or the factory returns ``None``.
        """
        if self._vpn_client_factory is None:
            err_msg_lines = ["No VPN client factory configured for managed host."]
            err_msg_lines.append("PROVIDER: {}".format(self._provider))
            err_msg_lines.append("DEVICE:   {}".format(self._device_identifier(device)))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        client = self._vpn_client_factory(device=device, provider=self._provider)
        if client is None:
            err_msg_lines = ["VPN client factory returned None for managed host."]
            err_msg_lines.append("PROVIDER: {}".format(self._provider))
            err_msg_lines.append("DEVICE:   {}".format(self._device_identifier(device)))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        register = getattr(device, "register_vpn_client", None)
        if register is not None:
            register(provider=self._provider, client=client)
        else:
            registry = getattr(device, "_vpn_clients", None)
            if registry is None:
                registry = {}
                setattr(device, "_vpn_clients", registry)
            registry[self._provider] = client
        return

    def _match_device(self, *, device: Any,
                      index: Dict[str, VPNDeviceRecord],
                      records: List[VPNDeviceRecord],
                      aspects: AspectsLandscapeCoupling,
                      ambiguous_acc: List[str]) -> Optional[VPNDeviceRecord]:
        """
            Resolve the best control-plane record for a landscape
            device.

            Hostname matches are preferred over tag matches. A tag match
            that resolves to multiple records is either raised or
            recorded depending on ``aspects.raise_on_ambiguous``.

            :param device: The landscape device.
            :param index: The hostname index.
            :param records: The full list of control plane records, used
                for tag matching.
            :param aspects: The landscape coupling aspects.
            :param ambiguous_acc: Accumulator for ambiguous-match device
                identifiers (lenient mode only).

            :returns: The matching :class:`VPNDeviceRecord`, or ``None``
                when no unambiguous match could be found.

            :raises: :class:`VPNCoordinatorAmbiguousMatchError` when a
                tag match resolves to multiple records and
                ``aspects.raise_on_ambiguous`` is ``True``.
        """
        hostname = self._normalise_hostname(self._device_hostname(device))
        hostname_match: Optional[VPNDeviceRecord] = None
        if hostname is not None and hostname in index:
            hostname_match = index[hostname]

        tags = self._device_tags(device)
        tag_matches: List[VPNDeviceRecord] = []
        if len(tags) > 0:
            tag_matches = self._records_matching_any_tag(tags, records)

        rtnval: Optional[VPNDeviceRecord] = None

        if hostname_match is not None:
            if len(tag_matches) > 0:
                other_ids = []
                for tm in tag_matches:
                    if tm.device_id != hostname_match.device_id:
                        other_ids.append(tm.device_id)
                if len(other_ids) > 0:
                    info_msg = ("Device '{}' matched on hostname; ignoring tag matches: {}"
                                .format(self._device_identifier(device), other_ids))
                    logger.info(info_msg)
            rtnval = hostname_match
        elif len(tag_matches) == 1:
            rtnval = tag_matches[0]
        elif len(tag_matches) > 1:
            candidate_ids = [tm.device_id for tm in tag_matches]
            if aspects.raise_on_ambiguous:
                err_msg_lines = ["Tag match resolved to multiple VPN device records."]
                err_msg_lines.append("DEVICE:   {}".format(self._device_identifier(device)))
                err_msg_lines.append("PROVIDER: {}".format(self._provider))
                err_msg_lines.append("CANDIDATES:")
                for cid in candidate_ids:
                    err_msg_lines.append("    {}".format(cid))
                err_msg = os.linesep.join(err_msg_lines)
                raise VPNCoordinatorAmbiguousMatchError(err_msg)
            else:
                ambiguous_acc.append(self._device_identifier(device))
                rtnval = None
        else:
            rtnval = None

        return rtnval

    def couple(self, *, devices: List[Any],
               aspects: AspectsLandscapeCoupling = DEFAULT_LANDSCAPE_COUPLING_ASPECTS
               ) -> VPNCouplingResult:
        """
            Walk ``devices`` and populate overlay addresses from the
            VPN control plane.

            The control plane is queried exactly once per ``couple``
            invocation. Devices whose match returns a record with
            ``overlay_address=None`` (Twingate asymmetry) are skipped
            without mutation and logged at DEBUG. Devices that already
            carry the matching overlay address are skipped (idempotent
            contract).

            :param devices: The landscape devices to consider.
            :param aspects: Behaviour control for the call. Defaults to
                :data:`DEFAULT_LANDSCAPE_COUPLING_ASPECTS`.

            :returns: A :class:`VPNCouplingResult` summarising the
                outcome.

            :raises: :class:`VPNCoordinatorAmbiguousMatchError` when a
                tag match is ambiguous and
                ``aspects.raise_on_ambiguous`` is ``True``.
            :raises: :class:`ConfigurationError` when a device declares
                ``vpn.managed=True`` and no client factory is configured.
        """
        cp_aspects = self._aspects_for_control_plane(aspects)
        records = self._control_plane.list_devices(aspects=cp_aspects)

        index = self._build_index(records)

        result = VPNCouplingResult(provider=self._provider)

        for device in devices:
            match = self._match_device(device=device, index=index,
                                       records=records, aspects=aspects,
                                       ambiguous_acc=result.ambiguous_tag_matches)

            if match is None:
                result.unmatched = result.unmatched + 1
                debug_msg = ("Device '{}' had no VPN peer match for provider '{}'."
                             .format(self._device_identifier(device), self._provider))
                logger.debug(debug_msg)
                continue

            candidate_address = match.overlay_address
            if candidate_address is None:
                result.skipped = result.skipped + 1
                debug_msg = ("Skipping overlay write for device '{}': provider '{}' "
                             "returned overlay_address=None (Twingate asymmetry)."
                             .format(self._device_identifier(device), self._provider))
                logger.debug(debug_msg)
                continue

            mutated = self._apply_overlay(device=device, address=candidate_address)
            if mutated:
                result.updated = result.updated + 1
            else:
                result.skipped = result.skipped + 1

            managed = self._device_managed(device, default=self._vpn_managed_default)
            if managed:
                already_registered = self._has_registered_vpn_client(device=device)
                if not already_registered:
                    self._register_vpn_client(device=device)

        return result

    def refresh(self, *, devices: List[Any],
                aspects: AspectsLandscapeCoupling = DEFAULT_LANDSCAPE_COUPLING_ASPECTS
                ) -> VPNCouplingResult:
        """
            Re-query the control plane and reconcile overlay addresses.

            ``refresh`` is semantically equivalent to :meth:`couple`:
            the control plane is queried, the index is rebuilt, and
            devices whose overlay slot already matches are skipped.

            :param devices: The landscape devices to reconcile.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`VPNCouplingResult` summarising the
                outcome.
        """
        rtnval = self.couple(devices=devices, aspects=aspects)
        return rtnval

    def decouple(self, *, devices: List[Any],
                 aspects: AspectsLandscapeCoupling = DEFAULT_LANDSCAPE_COUPLING_ASPECTS
                 ) -> None:
        """
            Clear the overlay slot for the coupling's provider on every
            device in ``devices``.

            The PUBLIC and PRIVATE slots are not touched.

            :param devices: The landscape devices to decouple.
            :param aspects: Behaviour control for the call (currently
                unused by ``decouple`` but accepted to preserve the
                landscape coupling contract).
        """
        _ = aspects
        for device in devices:
            address_set = device.addresses
            existing = address_set.overlay(provider=self._provider)
            if existing is not None:
                address_set.set_overlay(provider=self._provider, address=None)
        return


__all__ = [
    "VPNCoordinatorCoupling",
    "VPN_COORDINATOR_COUPLING_KIND",
    "register_coupling_kind",
    "coupling_type_for_kind",
    "is_coupling_kind_registered",
]
