"""
    .. module:: landscapedevice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeDevice` class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import Callable, Dict, Union, TYPE_CHECKING

from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import os
import socket
import threading
import weakref

from datetime import datetime

from automojo.errors.exceptions import AbstractMethodError, ConfigurationError, SemanticError

from automojo.credentials.basecredential import BaseCredential
from automojo.credentials.sshcredential import SshCredential
from automojo.interfaces.addressplane import AddressPlane
from automojo.interop.interfaces.isystemcontext import ISystemContext
from automojo.landscaping.addressing.deviceaddressset import DeviceAddressSet
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier
from automojo.landscaping.extensions.protocol.protocolextension import ProtocolExtension
from automojo.xmodules.xthreading.lockscopes import LockedScope, UnLockedScope

from automojo.testbase.features import FeatureAttachedObject

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinatorbase import CoordinatorBase

class LandscapeDevice(FeatureAttachedObject):
    """
        The base class for all landscape devices.  The :class:`LandscapeDevice' represents attributes that are common
        to all connected devices and provides attachements points and mechanisms for adding DeviceExtentions to
        the :class:`LandscapeDevice` device.
    """

    # Base landscape devices don't have any feature tags, but we want all devices to have feature
    # tag capability so we can filter all devices based on feature tags, whether they have
    # tags or not.
    FEATURE_TAGS = []

    logger = getEnhancedLogger()

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase", friendly_id:
                 FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Constructs a new :class:`LandscapeDevice` instance.

            :param lscape: The :class:`Landscape` this device belongs to.
            :param coordinator: Coordinator responsible for the device.
            :param friendly_id: A :class:`FriendlyIdentifier` for the device.
            :param device_type: The declared device type.
            :param device_config: Configuration dictionary for the device.
        """
        super().__init__()

        # These data items live for the life of the device, so they are not guarded
        # by a lock
        self._lscape_ref = weakref.ref(lscape)
        self._coord_ref = weakref.ref(coordinator)

        self._friendly_id = friendly_id
        self._device_type = device_type
        self._device_config = device_config

        # Devices can have a group assigned to support collections of devices
        # like clusters, for clusters giving a device a group does not assign
        # automatincaly group the device into a cluster.  It just means the
        # device is eligible to belong to a given cluster.
        self._group = ""
        if "group" in device_config:
            self._group = device_config["group"]

        self._device_lock = threading.RLock()

        self._contacted_first = None
        self._contacted_last = None
        self._is_watched = None
        self._is_isolated = None

        self._extensions: Dict[str, ProtocolExtension] = {}

        self._table_for_match_callbacks = {}
        self._table_for_status_callbacks = {}

        self._credentials = {}

        self._name = None
        if "name" in device_config:
            self._name = device_config["name"]
        
        self._role = None
        if "role" in device_config:
            self._role = device_config["role"]

        self._features = {}
        if "features" in device_config:
             self._features = device_config["features"]

        self._host = None
        if "host" in self._device_config:
            self._host = self._device_config["host"]

        self._configured_ipaddr = None
        if "ipaddr" in device_config:
            self._configured_ipaddr = device_config["ipaddr"]

        # Multi-plane address set. The legacy ``_host`` value populates
        # the PUBLIC slot to preserve today's behaviour for any caller
        # reading addresses through the new ``addresses`` property.
        self._address_set = DeviceAddressSet(public=self._host)

        # Per-device preferred plane. Default is PUBLIC, which keeps the
        # legacy behaviour bit-identical. Per-device config may override;
        # landscape-root fallback is consulted when the device omits it.
        self._preferred_plane = self._determine_preferred_plane(lscape=lscape,
                                                                device_config=device_config)

        # Landscape VPN per-device override fields. These default to
        # empty/None so legacy device configurations remain bit-identical.
        self._vpn_provider = None
        self._vpn_managed = False
        self._vpn_advertise_tags = []
        self._initialize_vpn_overrides(device_config=device_config)

        self._overlay_warning_emitted = False

        if self._configured_ipaddr is None and self._host is not None:
             self._resolve_ipaddress()

        credmgr = lscape.credential_manager

        if "credentials" in device_config:
            for cred_key in device_config["credentials"]:
                self._credentials[cred_key] = credmgr.lookup_credential(cred_key)

        self._has_ssh_credential = False
        self._ssh_credential = None
        for cred in self._credentials.values():
            if isinstance(cred, SshCredential):
                self._has_ssh_credential = True
                self._ssh_credential = cred
                break

        return

    @property
    def addresses(self) -> DeviceAddressSet:
        """
            Returns the multi-plane :class:`DeviceAddressSet` carried by
            this device.

            :returns: The device's :class:`DeviceAddressSet` instance.
        """
        rtnval = self._address_set
        return rtnval

    @property
    def vpn_provider(self) -> Union[str, None]:
        """
            Returns the name of the landscape root ``vpn.providers``
            entry this device is bound to, or ``None`` when the device
            has no per-device VPN override.

            :returns: The provider name or ``None``.
        """
        rtnval = self._vpn_provider
        return rtnval

    @property
    def vpn_managed(self) -> bool:
        """
            Returns ``True`` when the device opted in to landscape-managed
            VPN-daemon ownership via ``devices[*].vpn.managed``.

            :returns: The managed flag (default ``False``).
        """
        rtnval = self._vpn_managed
        return rtnval

    @property
    def vpn_advertise_tags(self) -> list:
        """
            Returns the per-device advertise-tag list. Empty when the
            device did not declare ``devices[*].vpn.advertise_tags``.

            :returns: A list of advertised tag strings.
        """
        rtnval = list(self._vpn_advertise_tags)
        return rtnval

    @property
    def preferred_plane(self) -> AddressPlane:
        """
            Returns the preferred :class:`AddressPlane` to use when
            dialing this device. Default is :attr:`AddressPlane.PUBLIC`.

            :returns: The configured preferred plane.
        """
        rtnval = self._preferred_plane
        return rtnval

    @property
    def configured_ipaddr(self) -> Union[str, None]:
        """
            Returns the IP address configured for the device if specified.
        """
        return self._configured_ipaddr

    @property
    def contacted_first(self) -> datetime:
        """
            A datetime stamp of when this device was first contacted
        """
        return self._contacted_first

    @property
    def contacted_last(self) -> datetime:
        """
            A datetime stamp of when this device was last contacted
        """
        return self._contacted_last

    @property
    def coordinator(self) -> "CoordinatorBase":
        """
            Returns the coordinator object managing this device.
        """
        return self._coord_ref()

    @property
    def credentials(self) -> Dict[str, BaseCredential]:
        """
            Dictionary of credentials keyed by name for this device.
        """
        return self._credentials

    @property
    def device_config(self) -> dict:
        """
            A dictionary of the configuration information for this device.
        """
        return self._device_config

    @property
    def device_type(self) -> str:
        """
            A string representing the type of device.
        """
        return self._device_type

    @property
    def extensions(self) -> Dict[str, ProtocolExtension]:
        """
            Returns a shallow copy of the protocol extensions for the device.
        """
        extdict = self._extensions.copy()
        return extdict

    @property
    def friendly_id(self) -> FriendlyIdentifier:
        """
            The friendly identifier for this device, this is generally the identifier provided
            by the coordinator that created the device instance.
        """
        return self._friendly_id

    @property
    def full_identifier(self) -> str:
        """
            The full identifier for this device, if one has been resolved.
        """
        return self._friendly_id.full_identifier

    @property
    def group(self) -> str:
        """
            A string represeting the group a device has been assigned to.
        """
        return self._group

    @property
    def has_ssh_credential(self) -> bool:
        """
            Indicates if a device has and SshCredential associated with it.
        """
        return self._has_ssh_credential

    @property
    def identity(self) -> str:
        """
            Returns a string that identifies a device in logs. This property can
            be overridden by custom landscape devices to customize identities in
            logs.
        """
        return self._friendly_id.identity

    @property
    def ipaddr(self) -> str:
        """
            The device IP of the device, if available.
        """
        ipaddr = self._resolve_ipaddress()
        return ipaddr

    @property
    def is_configured_for_power(self):
        """
            Indicates if this device has power control configured.

            :returns: ``True`` if power control is available.
        """
        rtnval = True if "power" in self._features else False
        return rtnval
    
    @property
    def is_configured_for_serial(self):
        """
            Indicates if this device has serial connectivity configured.

            :returns: ``True`` if serial connectivity is available.
        """
        rtnval = True if "serial" in self._features else False
        return rtnval

    @property
    def is_watched(self) -> bool:
        """
            A boolean indicating if this device is a watched device.
        """
        return self._is_watched

    @property
    def landscape(self) -> "Landscape":
        """
            Returns a strong reference to the the landscape object
        """
        return self._lscape_ref()

    @property
    def moniker(self) -> str:
        """
            Returns a moniker for this device.
        """
        return self._friendly_id.identity

    @property
    def name(self) -> str:
        """
            A string representing a name for the devices 
        """
        return self._name

    @property
    def pivots(self) -> str:
        """
            Returns a set of pivot data points that can be used to
            colate results.
        """
        pivots = (self._friendly_id.identity,)
        return pivots

    @property
    def role(self) -> str:
        """
            A string representing a role assigned to the device 
        """
        return self._role

    @property
    def ssh_credential(self) -> Union[SshCredential, None]:
        """
            Returns the primary SSH credential for the device if present.
        """
        return self._ssh_credential

    def attach_extension(self, ext_type: str, extension: ProtocolExtension) -> None:
        """
            Method called by device coordinators to attach a device extension to a :class:`LandscapeDevice`.
        """

        if ext_type not in self._extensions:
            self._extensions[ext_type] = extension
        else:
            if self._extensions[ext_type] is extension:
                return

            errmsg = f"attach_extension: called for pre-existing extension type '{ext_type}'."
            raise SemanticError(errmsg)

        return

    def begin_locked_scope(self) -> "LockedScope":
        """
            Method that creates a locked scope for this device.
        """
        lkd_scope = LockedScope(self._device_lock)
        return lkd_scope

    def begin_unlocked_scope(self) -> "UnLockedScope":
        """
            Method that creates an unlocked scope for this device.
        """
        unlkd_scope = UnLockedScope(self._device_lock)
        return unlkd_scope

    def checkout(self) -> None:
        """
            Method that makes it convenient to checkout device.
        """
        self.landscape.checkout_device(self)
        return

    def checkin(self) -> None:
        """
            Method that makes it convenient to checkin a device.
        """
        self.landscape.checkin_device(self)
        return

    def attach_to_power(self):
        """
            Called to allow a device to attach to the power management resources.
        """
        if self.is_configured_for_power:
            power_config = self._features["power"]

            # We need to filter the configuration to only include the keys that are
            # used to identify the power control point.  Extra keys in the configuration
            # can cause the checkout key generation to fail to match the key registered
            # by the coordinator.
            server = power_config["server"]
            outlet = int(power_config["outlet"])

            power_ext = self.landscape.checkout_control_point("power", server=server, outlet=outlet)

            # The extension is already created and initialized by the coordinator
            # We just need to update the reference to the device it is extending
            power_ext.update_extends_ref(weakref.ref(self))

            self.attach_extension("power", power_ext)

        return

    def attach_to_serial(self):
        """
            Called to allow a device to attach to the serial connectivity resources.
        """
        if self.is_configured_for_serial:
            serial_config = self._features["serial"]

            # We need to filter the configuration to only include the keys that are
            # used to identify the serial control point.  Extra keys in the configuration
            # can cause the checkout key generation to fail to match the key registered
            # by the coordinator.
            host = serial_config["host"]
            port = int(serial_config["port"])

            serial_ext = self.landscape.checkout_control_point("serial", host=host, port=port)

            # The extension is already created and initialized by the coordinator
            # We just need to update the reference to the device it is extending
            serial_ext.update_extends_ref(weakref.ref(self))

            self.attach_extension("serial", serial_ext)

        return

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return

    def get_credentials_by_category(self, category: str):
        """
            Gets a list of credentials that are associated with a specific category.
        """
        cred_list = []

        for cred in self._credentials.values():
            if category in cred.categories:
                cred_list.append(cred)

        return cred_list

    def get_default_system_context(self) -> ISystemContext:
        """
            Called to get an ISystemContext instance that is a default system type.
        """
        type_name = type(self).__name__
        raise AbstractMethodError(f"get_default_system_context: not overloaded for type='{type_name}'")

    def has_extension_type(self, ext_type: str) -> bool:
        """
            Returns a boolean value indicating if this device has the specified extension
            type registered.
        """
        has_ext_type = False
        if ext_type in self._extensions:
            has_ext_type = True
        return has_ext_type

    def initialize_credentials(self, credentials: Dict[str, BaseCredential]) -> None:
        """
            Initializes the credentials of the device based on the credentials listed for
            the device in the device configuration and the credentials configuration.
        """
        self._credentials = credentials
        return

    def initialize_features(self) -> None:
        """
            Initializes the features of the device based on the feature declarations and the information
            found in the feature config.
        """
        if "features" in self._device_config:
            feature_info = self._device_config["features"]
            for fkey, fval in feature_info.items():
                if fkey == "isolation":
                    self._is_isolated = fval
                elif fkey == "":
                    pass
        return

    def match_using_params(self, match_type, *match_params) -> bool:
        """
            Method that allows you to match :class:`LandscapeDevice` objects by providing a match_type and
            parameters.  The match type is mapped to functions that are registered by device coordinators
            and then the function is called with the match parameters to determine if a device is a match.
        """
        matches = False
        match_func = None
        match_self = None

        with self.begin_locked_scope() as lk_locked:

            if match_type in self._table_for_match_callbacks:
                dext_attr, match_func = self._table_for_match_callbacks[match_type]
                match_self = None
                if hasattr(self, dext_attr):
                    match_self = getattr(self, dext_attr)

        if match_self is not None and match_func is not None:
            matches = match_func(match_self, *match_params)

        return matches


    def update_full_identifier(self, full_identifier: str) -> None:
        """
            Update the full identifier associated with the FriendlyIdentifier for this device.
        """

        self._friendly_id.update_full_identifier(full_identifier)
        
        return

    def update_match_table(self, match_table: dict) -> None:
        """
            Method called  to update the match functions.
        """

        with self.begin_locked_scope() as lk_locked:

            self._table_for_match_callbacks.update(match_table)

        return
    
    def update_status_verification_callback(self, protocol: str, status_callback: Callable) -> None:
        """
            Method called  to update the verification callback functions for a given protocol.
        """

        with self.begin_locked_scope() as lk_locked:

            self._table_for_status_callbacks[protocol] = status_callback

        return

    def verify_status(self) -> None:
        """
            Verify the status of the specified device.
        """

        with self.begin_locked_scope() as lk_locked:

            for protocol, verify_status_callback in self._table_for_status_callbacks.items():
                verify_status_callback()

        return

    def _resolve_ipaddress(self) -> str:
        """
            Resolves and caches the IP address for this device using the host
            or configured IP address. The resolved address is also mirrored
            into the multi-plane address set's PUBLIC slot so consumers of
            :attr:`addresses` observe the same value.

            :returns: The resolved IPv4/IPv6 address as a string.
            :raises: :class:`ConfigurationError` when DNS resolution fails;
                :class:`RuntimeError` when neither host nor configured
                ipaddr is available.
        """

        ipaddr = None

        if self._configured_ipaddr is not None:
            ipaddr = self._configured_ipaddr
        elif self._host is not None:
            try:
                ipaddr = socket.gethostbyname(self._host)
                self._configured_ipaddr = ipaddr
            except (socket.gaierror, OSError):
                errmsg = f"Unable to resolve ipaddr for host={self._host}, contact information for devices must be valid."
                self.logger.error(errmsg)
                raise ConfigurationError(errmsg)
        else:
            errmsg = f"_resolve_ipaddress: Unable to resolve IP address for dev {self}."
            raise RuntimeError(errmsg)

        # Mirror the resolved address into the PUBLIC slot of the
        # multi-plane address set. The original ``_host`` value is
        # preserved as a fallback when DNS resolution did not happen.
        public_for_set = ipaddr
        if public_for_set is None:
            public_for_set = self._host
        self._address_set.set_public(address=public_for_set)

        return ipaddr

    def _resolve_addresses(self) -> DeviceAddressSet:
        """
            Refresh and return the device's multi-plane address set.

            For now this method only populates the PUBLIC slot (from the
            existing DNS/configured-ipaddr path). Future M4 work will
            extend it to populate PRIVATE and OVERLAY slots from cloud
            metadata and VPN coordinators respectively.

            :returns: The :class:`DeviceAddressSet` carried by this device.
        """
        if self._configured_ipaddr is None and self._host is not None:
            self._resolve_ipaddress()
        elif self._address_set.public() is None and self._host is not None:
            self._address_set.set_public(address=self._host)

        if self._preferred_plane == AddressPlane.OVERLAY:
            overlay_addr = self._address_set.overlay()
            if overlay_addr is None and not self._overlay_warning_emitted:
                warn_msg = ("Device {} has preferred_plane=OVERLAY but no "
                            "overlay address is populated; falling back to "
                            "the public plane.").format(self.identity)
                self.logger.warning(warn_msg)
                self._overlay_warning_emitted = True

        rtnval = self._address_set
        return rtnval

    def _determine_preferred_plane(self, *, lscape: "Landscape",
                                   device_config: dict) -> AddressPlane:
        """
            Resolve the device's preferred address plane from per-device
            config with landscape-root fallback.

            :param lscape: The landscape this device belongs to.
            :param device_config: The device's configuration dictionary.

            :returns: The resolved :class:`AddressPlane` value. Default
                is :attr:`AddressPlane.PUBLIC`.
        """
        rtnval = AddressPlane.PUBLIC

        configured = None
        if "preferred_plane" in device_config:
            configured = device_config["preferred_plane"]
        elif "vpn" in device_config and isinstance(device_config["vpn"], dict) \
                and "preferred_plane" in device_config["vpn"]:
            # Per-device override expressed as ``devices[*].vpn.preferred_plane``
            # per the landscape-vpn-config-schema spec.
            configured = device_config["vpn"]["preferred_plane"]
        else:
            # Landscape-root fallback. The attribute may not exist on
            # older landscape implementations, so look it up defensively.
            # The schema-driven attribute name is ``vpn_default_plane``;
            # the legacy attribute ``preferred_plane`` is honoured as a
            # backward-compatible secondary.
            landscape_attr = getattr(lscape, "vpn_default_plane", None)
            if landscape_attr is None:
                landscape_attr = getattr(lscape, "preferred_plane", None)
            if landscape_attr is not None:
                configured = landscape_attr

        if configured is not None:
            if isinstance(configured, AddressPlane):
                rtnval = configured
            elif isinstance(configured, str):
                key = configured.strip().upper()
                if key in AddressPlane.__members__:
                    rtnval = AddressPlane[key]

        return rtnval

    def _initialize_vpn_overrides(self, *, device_config: dict) -> None:
        """
            Pull the per-device ``vpn:`` override values out of the raw
            configuration dictionary, populating ``_vpn_provider``,
            ``_vpn_managed`` and ``_vpn_advertise_tags`` accordingly.

            Devices without a ``vpn:`` mapping retain their defaults so
            existing landscape files behave bit-identically.

            :param device_config: The device configuration dictionary.
        """
        if "vpn" not in device_config:
            return

        vpn_block = device_config["vpn"]
        if not isinstance(vpn_block, dict):
            return

        if "provider" in vpn_block:
            provider_value = vpn_block["provider"]
            if isinstance(provider_value, str) and len(provider_value) > 0:
                self._vpn_provider = provider_value

        if "managed" in vpn_block:
            managed_value = vpn_block["managed"]
            if isinstance(managed_value, bool):
                self._vpn_managed = managed_value

        if "advertise_tags" in vpn_block:
            tags_value = vpn_block["advertise_tags"]
            if isinstance(tags_value, list):
                clean_tags: list = []
                for tag in tags_value:
                    if isinstance(tag, str):
                        clean_tags.append(tag)
                self._vpn_advertise_tags = clean_tags

        return

    def _repr_html_(self) -> str:
        """
            HTML representation used in interactive notebooks.
        """
        ipaddr = "unknown"
        if self._configured_ipaddr is not None:
            ipaddr = self._configured_ipaddr

        html_repr_lines = [
            "<h1>LandscapeDevice</h1>",
            "<h2>     type: {}</h2>".format(self._device_type),
            "<h2>    identity: {}</h2>".format(self.identity),
            "<h2>       ip: {}</h2>".format(ipaddr)
        ]

        html_repr = os.linesep.join(html_repr_lines)

        return html_repr

    def __repr__(self) -> str:
        """
            Returns a concise string representation for debugging.
        """

        thisType = type(self)

        ipaddr = "unknown"
        if self._configured_ipaddr is not None:
            ipaddr = self._configured_ipaddr

        devstr = "<{} type={} identity={} ip={} >".format(thisType.__name__, self._device_type, self.identity, ipaddr)

        return devstr

    def __str__(self) -> str:
        """
            Returns a user friendly string representation of the device.
        """
        devstr = repr(self)
        return devstr
