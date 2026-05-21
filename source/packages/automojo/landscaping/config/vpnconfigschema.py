"""
    .. module:: vpnconfigschema
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Landscape-level schema validator and parser for the
                   ``vpn:`` block in ``landscape.yaml``.

        This module is the landscape-tier counterpart to
        :mod:`automojo.configuration.schemas.vpnconfigschema`. It validates
        the structure of the ``vpn:`` block embedded in a landscape document
        (including per-device ``devices[*].vpn`` overrides), emits structured
        diagnostics, and parses the canonical form into typed entries that
        the landscape construction code consumes.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any, Dict, List, Optional, Tuple

from automojo.interfaces.addressplane import AddressPlane

from automojo.landscaping.config.landscapeconfigdiagnostic import (
    LandscapeConfigDiagnostic,
    LandscapeConfigError,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
)
from automojo.landscaping.config.vpnproviderentry import VPNProviderEntry


# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

ACCEPTED_VPN_KINDS: Tuple[str, ...] = ("tailscale", "twingate")

ACCEPTED_DEFAULT_PLANES: Tuple[str, ...] = ("PUBLIC", "PRIVATE", "OVERLAY")

ROOT_VPN_KNOWN_KEYS: Tuple[str, ...] = ("default_plane", "providers")

PROVIDER_KNOWN_KEYS: Tuple[str, ...] = (
    "name",
    "kind",
    "credential_ref",
    "tailnet",
    "network_slug",
    "default_tags",
)

DEVICE_VPN_KNOWN_KEYS: Tuple[str, ...] = (
    "provider",
    "managed",
    "advertise_tags",
    "preferred_plane",
)


def validate_landscape_vpn_block(*, doc: dict) -> List[LandscapeConfigDiagnostic]:
    """
        Validate the ``vpn:`` block (and ``devices[*].vpn`` overrides)
        within a parsed landscape document.

        :param doc: The parsed landscape document (the top-level mapping
            from ``landscape.yaml``).

        :returns: A list of :class:`LandscapeConfigDiagnostic` records. An
            empty list indicates the block validates cleanly. The list may
            contain a mix of ``error`` and ``warning`` severities; callers
            who want a hard-fail should raise on any ``error`` severity.
    """
    diagnostics: List[LandscapeConfigDiagnostic] = []

    if doc is None:
        return diagnostics

    if "vpn" not in doc:
        # Per design.md step 1: absent vpn block produces an empty diagnostics list.
        # Per-device ``vpn`` blocks that reference a missing root are still
        # validated below for symmetry.
        _validate_device_overrides(doc=doc,
                                   provider_names=set(),
                                   diagnostics=diagnostics)
        return diagnostics

    vpn_section = doc["vpn"]

    if not isinstance(vpn_section, dict):
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path="vpn",
            message="The 'vpn' section must be a mapping.",
        )
        diagnostics.append(diag)
        return diagnostics

    _validate_default_plane(vpn_section=vpn_section, diagnostics=diagnostics)

    provider_names = _validate_providers(vpn_section=vpn_section,
                                         diagnostics=diagnostics)

    _validate_unknown_root_keys(vpn_section=vpn_section, diagnostics=diagnostics)

    _validate_device_overrides(doc=doc,
                               provider_names=provider_names,
                               diagnostics=diagnostics)

    return diagnostics


def parse_landscape_vpn_block(*, doc: dict) -> Tuple[AddressPlane, List[VPNProviderEntry]]:
    """
        Validate then parse the ``vpn:`` block from a landscape document
        into its canonical typed form.

        :param doc: The parsed landscape document.

        :returns: A 2-tuple ``(default_plane, providers)`` where
            ``default_plane`` is the root-level :class:`AddressPlane`
            (defaulting to :attr:`AddressPlane.PUBLIC` when the block is
            absent or did not specify one) and ``providers`` is the
            ordered list of :class:`VPNProviderEntry` records (empty when
            the block is absent).
        :raises: :class:`LandscapeConfigError` when any ``error``-severity
            diagnostic is produced. Warning-severity diagnostics do not
            cause this function to raise.
    """
    diagnostics = validate_landscape_vpn_block(doc=doc)

    error_diags: List[LandscapeConfigDiagnostic] = []
    for diag in diagnostics:
        if diag.severity == SEVERITY_ERROR:
            error_diags.append(diag)

    if len(error_diags) > 0:
        err_msg_lines = ["Landscape vpn-config-schema validation failed:"]
        for diag in error_diags:
            err_msg_lines.append("  - [{}] {}: {}".format(diag.severity,
                                                          diag.path,
                                                          diag.message))
        err_msg = os.linesep.join(err_msg_lines)
        raise LandscapeConfigError(err_msg)

    default_plane = AddressPlane.PUBLIC
    providers: List[VPNProviderEntry] = []

    if doc is None:
        rtnval = (default_plane, providers)
        return rtnval

    if "vpn" not in doc:
        rtnval = (default_plane, providers)
        return rtnval

    vpn_section = doc["vpn"]

    if "default_plane" in vpn_section:
        raw_plane = vpn_section["default_plane"]
        if isinstance(raw_plane, str):
            key = raw_plane.strip().upper()
            if key in AddressPlane.__members__:
                default_plane = AddressPlane[key]

    providers_raw = vpn_section.get("providers", [])
    if isinstance(providers_raw, list):
        for entry in providers_raw:
            if not isinstance(entry, dict):
                continue
            provider_entry = _build_provider_entry(entry=entry)
            if provider_entry is not None:
                providers.append(provider_entry)

    rtnval = (default_plane, providers)
    return rtnval


def warnings_from(*, diagnostics: List[LandscapeConfigDiagnostic]) -> List[LandscapeConfigDiagnostic]:
    """
        Filter ``warning``-severity diagnostics out of a diagnostics list.

        :param diagnostics: A list of :class:`LandscapeConfigDiagnostic`.

        :returns: The subset whose ``severity`` is ``"warning"``.
    """
    warnings: List[LandscapeConfigDiagnostic] = []
    for diag in diagnostics:
        if diag.severity == SEVERITY_WARNING:
            warnings.append(diag)
    return warnings


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_default_plane(*, vpn_section: dict,
                            diagnostics: List[LandscapeConfigDiagnostic]) -> None:
    """
        Validate ``vpn.default_plane`` and append diagnostics on failure.

        :param vpn_section: The raw ``vpn:`` mapping.
        :param diagnostics: Mutable diagnostics list to append to.
    """
    if "default_plane" not in vpn_section:
        return

    raw = vpn_section["default_plane"]

    if not isinstance(raw, str):
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path="vpn.default_plane",
            message="vpn.default_plane must be a string.",
        )
        diagnostics.append(diag)
        return

    key = raw.strip().upper()
    if key not in ACCEPTED_DEFAULT_PLANES:
        msg = ("vpn.default_plane must be one of {}; got {!r}.").format(
            list(ACCEPTED_DEFAULT_PLANES), raw)
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path="vpn.default_plane",
            message=msg,
        )
        diagnostics.append(diag)

    return


def _validate_providers(*, vpn_section: dict,
                        diagnostics: List[LandscapeConfigDiagnostic]) -> set:
    """
        Validate ``vpn.providers`` and return the set of accepted
        provider names.

        :param vpn_section: The raw ``vpn:`` mapping.
        :param diagnostics: Mutable diagnostics list to append to.

        :returns: The set of provider names that passed validation; this
            set seeds the per-device ``provider`` cross-reference check.
    """
    provider_names: set = set()

    if "providers" not in vpn_section:
        return provider_names

    providers_raw = vpn_section["providers"]

    if not isinstance(providers_raw, list):
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path="vpn.providers",
            message="vpn.providers must be a list.",
        )
        diagnostics.append(diag)
        return provider_names

    for idx in range(0, len(providers_raw)):
        entry = providers_raw[idx]
        _validate_provider_entry(entry=entry,
                                 idx=idx,
                                 provider_names=provider_names,
                                 diagnostics=diagnostics)

    return provider_names


def _validate_provider_entry(*, entry: Any, idx: int,
                             provider_names: set,
                             diagnostics: List[LandscapeConfigDiagnostic]) -> None:
    """
        Validate a single ``vpn.providers[idx]`` entry.

        :param entry: The raw entry.
        :param idx: The zero-based index of the entry.
        :param provider_names: Mutable set of accepted provider names.
        :param diagnostics: Mutable diagnostics list to append to.
    """
    base_path = "vpn.providers[{}]".format(idx)

    if not isinstance(entry, dict):
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path=base_path,
            message="provider entry must be a mapping.",
        )
        diagnostics.append(diag)
        return

    required = ("name", "kind", "credential_ref")
    missing: List[str] = []
    for key in required:
        if key not in entry:
            missing.append(key)

    if len(missing) > 0:
        msg = "provider entry missing required keys: {!r}.".format(missing)
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path=base_path,
            message=msg,
        )
        diagnostics.append(diag)
        return

    kind_value = entry["kind"]
    if kind_value not in ACCEPTED_VPN_KINDS:
        msg = ("provider kind must be one of {}; got {!r}.").format(
            list(ACCEPTED_VPN_KINDS), kind_value)
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path=base_path + ".kind",
            message=msg,
        )
        diagnostics.append(diag)
        return

    if kind_value == "tailscale":
        tailnet = entry.get("tailnet")
        if not isinstance(tailnet, str) or len(tailnet) == 0:
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=base_path + ".tailnet",
                message="tailscale providers require a non-empty 'tailnet'.",
            )
            diagnostics.append(diag)
            return
    elif kind_value == "twingate":
        network_slug = entry.get("network_slug")
        if not isinstance(network_slug, str) or len(network_slug) == 0:
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=base_path + ".network_slug",
                message="twingate providers require a non-empty 'network_slug'.",
            )
            diagnostics.append(diag)
            return

    name_value = entry["name"]
    if not isinstance(name_value, str) or len(name_value) == 0:
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path=base_path + ".name",
            message="provider 'name' must be a non-empty string.",
        )
        diagnostics.append(diag)
        return

    cred_ref = entry["credential_ref"]
    if not isinstance(cred_ref, str) or len(cred_ref) == 0:
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path=base_path + ".credential_ref",
            message="provider 'credential_ref' must be a non-empty string.",
        )
        diagnostics.append(diag)
        return

    # Unknown leaf-key tolerance (warning only).
    for raw_key in entry.keys():
        if raw_key not in PROVIDER_KNOWN_KEYS:
            msg = "unknown key {!r} on provider entry; ignored.".format(raw_key)
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_WARNING,
                path=base_path + "." + str(raw_key),
                message=msg,
            )
            diagnostics.append(diag)

    if name_value in provider_names:
        msg = ("duplicate provider name {!r}; provider names must be "
               "unique within vpn.providers.").format(name_value)
        diag = LandscapeConfigDiagnostic(
            severity=SEVERITY_ERROR,
            path=base_path + ".name",
            message=msg,
        )
        diagnostics.append(diag)
        return

    provider_names.add(name_value)

    return


def _validate_unknown_root_keys(*, vpn_section: dict,
                                diagnostics: List[LandscapeConfigDiagnostic]) -> None:
    """
        Emit a ``warning`` diagnostic for every unknown leaf key on the
        root ``vpn:`` mapping.

        :param vpn_section: The raw ``vpn:`` mapping.
        :param diagnostics: Mutable diagnostics list to append to.
    """
    for raw_key in vpn_section.keys():
        if raw_key not in ROOT_VPN_KNOWN_KEYS:
            msg = "unknown key {!r} on 'vpn' section; ignored.".format(raw_key)
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_WARNING,
                path="vpn." + str(raw_key),
                message=msg,
            )
            diagnostics.append(diag)
    return


def _validate_device_overrides(*, doc: dict, provider_names: set,
                               diagnostics: List[LandscapeConfigDiagnostic]) -> None:
    """
        Validate any per-device ``vpn:`` override blocks.

        The landscape doc tolerates two shapes:

        * a top-level ``devices:`` list (the test/spec shape).
        * the production ``apod:`` shape used by
          :class:`LandscapeConfigurationLayer`, where device sections are
          nested under ``apod`` and reserved sections are skipped.

        Both shapes are checked so the validator can be used from arcli
        and from the live loader.

        :param doc: The parsed landscape document.
        :param provider_names: Set of accepted root-provider names.
        :param diagnostics: Mutable diagnostics list to append to.
    """
    device_records = _collect_device_records(doc=doc)

    for path_prefix, device in device_records:
        if not isinstance(device, dict):
            continue
        if "vpn" not in device:
            continue

        vpn_block = device["vpn"]
        device_path = path_prefix + ".vpn"

        if not isinstance(vpn_block, dict):
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=device_path,
                message="device vpn override must be a mapping.",
            )
            diagnostics.append(diag)
            continue

        _validate_single_device_vpn(vpn_block=vpn_block,
                                    device_path=device_path,
                                    provider_names=provider_names,
                                    diagnostics=diagnostics)

    return


def _collect_device_records(*, doc: dict) -> List[Tuple[str, Any]]:
    """
        Collect a list of ``(path_prefix, device_dict)`` tuples covering
        every device-shaped entry under either the top-level ``devices:``
        list or under ``apod:<section>:``.

        :param doc: The parsed landscape document.

        :returns: List of ``(path_prefix, device)`` tuples in iteration
            order.
    """
    records: List[Tuple[str, Any]] = []

    if doc is None:
        return records

    devices_top = doc.get("devices")
    if isinstance(devices_top, list):
        for idx in range(0, len(devices_top)):
            entry = devices_top[idx]
            prefix = "devices[{}]".format(idx)
            records.append((prefix, entry))

    apod_section = doc.get("apod")
    if isinstance(apod_section, dict):
        reserved = {"controller"}
        for section_name in apod_section.keys():
            if section_name in reserved:
                continue
            section_items = apod_section[section_name]
            if not isinstance(section_items, list):
                continue
            for idx in range(0, len(section_items)):
                entry = section_items[idx]
                prefix = "apod.{}[{}]".format(section_name, idx)
                records.append((prefix, entry))

    return records


def _validate_single_device_vpn(*, vpn_block: dict, device_path: str,
                                provider_names: set,
                                diagnostics: List[LandscapeConfigDiagnostic]) -> None:
    """
        Validate one device-level ``vpn:`` override mapping.

        :param vpn_block: The device-level ``vpn:`` mapping.
        :param device_path: Dotted path prefix used for diagnostic
            ``path`` values.
        :param provider_names: Set of accepted root-provider names.
        :param diagnostics: Mutable diagnostics list to append to.
    """
    if "provider" in vpn_block:
        provider_name = vpn_block["provider"]
        if not isinstance(provider_name, str) or len(provider_name) == 0:
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=device_path + ".provider",
                message="device vpn.provider must be a non-empty string.",
            )
            diagnostics.append(diag)
        elif provider_name not in provider_names:
            msg = ("device vpn.provider {!r} does not match a declared "
                   "root provider name.").format(provider_name)
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=device_path + ".provider",
                message=msg,
            )
            diagnostics.append(diag)

    if "preferred_plane" in vpn_block:
        raw_plane = vpn_block["preferred_plane"]
        if not isinstance(raw_plane, str):
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=device_path + ".preferred_plane",
                message="device vpn.preferred_plane must be a string.",
            )
            diagnostics.append(diag)
        else:
            key = raw_plane.strip().upper()
            if key not in ACCEPTED_DEFAULT_PLANES:
                msg = ("device vpn.preferred_plane must be one of {}; "
                       "got {!r}.").format(list(ACCEPTED_DEFAULT_PLANES), raw_plane)
                diag = LandscapeConfigDiagnostic(
                    severity=SEVERITY_ERROR,
                    path=device_path + ".preferred_plane",
                    message=msg,
                )
                diagnostics.append(diag)

    if "managed" in vpn_block:
        managed_value = vpn_block["managed"]
        if not isinstance(managed_value, bool):
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=device_path + ".managed",
                message="device vpn.managed must be a boolean.",
            )
            diagnostics.append(diag)

    if "advertise_tags" in vpn_block:
        tags_value = vpn_block["advertise_tags"]
        if not isinstance(tags_value, list):
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_ERROR,
                path=device_path + ".advertise_tags",
                message="device vpn.advertise_tags must be a list of strings.",
            )
            diagnostics.append(diag)
        else:
            for tag_idx in range(0, len(tags_value)):
                tag_item = tags_value[tag_idx]
                if not isinstance(tag_item, str) or len(tag_item) == 0:
                    tag_path = "{}.advertise_tags[{}]".format(device_path, tag_idx)
                    diag = LandscapeConfigDiagnostic(
                        severity=SEVERITY_ERROR,
                        path=tag_path,
                        message="device vpn.advertise_tags entries must be non-empty strings.",
                    )
                    diagnostics.append(diag)

    for raw_key in vpn_block.keys():
        if raw_key not in DEVICE_VPN_KNOWN_KEYS:
            msg = "unknown key {!r} on device vpn override; ignored.".format(raw_key)
            diag = LandscapeConfigDiagnostic(
                severity=SEVERITY_WARNING,
                path=device_path + "." + str(raw_key),
                message=msg,
            )
            diagnostics.append(diag)

    return


def _build_provider_entry(*, entry: dict) -> Optional[VPNProviderEntry]:
    """
        Construct a :class:`VPNProviderEntry` from a validated raw entry.

        :param entry: The raw provider entry. Assumed to have already
            passed validation; missing keys produce ``None``.

        :returns: A :class:`VPNProviderEntry` on success, ``None`` on
            invalid input.
    """
    if "name" not in entry or "kind" not in entry or "credential_ref" not in entry:
        rtnval = None
        return rtnval

    name = entry["name"]
    kind = entry["kind"]
    credential_ref = entry["credential_ref"]

    tailnet = entry.get("tailnet")
    network_slug = entry.get("network_slug")

    raw_tags = entry.get("default_tags", [])
    default_tags: List[str] = []
    if isinstance(raw_tags, list):
        for tag in raw_tags:
            if isinstance(tag, str):
                default_tags.append(tag)

    rtnval = VPNProviderEntry(
        name=name,
        kind=kind,
        credential_ref=credential_ref,
        tailnet=tailnet,
        network_slug=network_slug,
        default_tags=default_tags,
    )
    return rtnval
