"""
    .. module:: test_vpnconfigschema
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for the landscape-level ``vpn:`` schema validator
                   and parser.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import unittest

from typing import Any, Dict

from ccai.interfaces.addressplane import AddressPlane

from ccai.landscaping.config.landscapeconfigdiagnostic import (
    LandscapeConfigDiagnostic,
    LandscapeConfigError,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
)
from ccai.landscaping.config.vpnconfigschema import (
    parse_landscape_vpn_block,
    validate_landscape_vpn_block,
    warnings_from,
)
from ccai.landscaping.config.vpnproviderentry import VPNProviderEntry


def _tailscale_doc() -> Dict[str, Any]:
    """
        Build a minimal landscape doc with one valid tailscale provider
        and no per-device overrides.

        :returns: A landscape-shaped dictionary.
    """
    rtnval = {
        "vpn": {
            "default_plane": "PUBLIC",
            "providers": [
                {
                    "name": "corp-tailnet",
                    "kind": "tailscale",
                    "credential_ref": "tailscale:corp",
                    "tailnet": "corp.example.com",
                    "default_tags": ["tag:lab"],
                },
            ],
        },
        "devices": [],
    }
    return rtnval


class NoVpnBlockTests(unittest.TestCase):
    """
        Backward compatibility — landscapes without ``vpn:``.
    """

    def test_no_vpn_block_returns_empty_diagnostics(self) -> None:
        """
            A doc with no ``vpn:`` key produces zero diagnostics.
        """
        doc: Dict[str, Any] = {"devices": []}
        diagnostics = validate_landscape_vpn_block(doc=doc)
        self.assertEqual(diagnostics, [])
        return

    def test_no_vpn_block_parses_defaults(self) -> None:
        """
            Parse returns ``(PUBLIC, [])`` when the block is absent.
        """
        doc: Dict[str, Any] = {"devices": []}
        default_plane, providers = parse_landscape_vpn_block(doc=doc)
        self.assertEqual(default_plane, AddressPlane.PUBLIC)
        self.assertEqual(providers, [])
        return

    def test_empty_doc_parses_defaults(self) -> None:
        """
            A wholly empty doc also parses to defaults.
        """
        default_plane, providers = parse_landscape_vpn_block(doc={})
        self.assertEqual(default_plane, AddressPlane.PUBLIC)
        self.assertEqual(providers, [])
        return


class TailscaleOnlyTests(unittest.TestCase):
    """
        Single tailscale provider, no devices.
    """

    def test_tailscale_only_parses_one_provider(self) -> None:
        """
            A tailscale-only block parses to exactly one provider.
        """
        doc = _tailscale_doc()
        default_plane, providers = parse_landscape_vpn_block(doc=doc)
        self.assertEqual(default_plane, AddressPlane.PUBLIC)
        self.assertEqual(len(providers), 1)
        entry = providers[0]
        self.assertEqual(entry.name, "corp-tailnet")
        self.assertEqual(entry.kind, "tailscale")
        self.assertEqual(entry.credential_ref, "tailscale:corp")
        self.assertEqual(entry.tailnet, "corp.example.com")
        self.assertEqual(entry.default_tags, ["tag:lab"])
        return

    def test_default_plane_overlay_round_trips(self) -> None:
        """
            ``default_plane: OVERLAY`` round-trips through the parser.
        """
        doc = _tailscale_doc()
        doc["vpn"]["default_plane"] = "OVERLAY"
        default_plane, _ = parse_landscape_vpn_block(doc=doc)
        self.assertEqual(default_plane, AddressPlane.OVERLAY)
        return


class InvalidKindTests(unittest.TestCase):
    """
        Hard-error paths.
    """

    def test_invalid_kind_raises_landscapeconfigerror(self) -> None:
        """
            An unknown provider ``kind`` raises ``LandscapeConfigError``.
        """
        doc = _tailscale_doc()
        doc["vpn"]["providers"][0]["kind"] = "wireguard"
        with self.assertRaises(LandscapeConfigError) as ctx:
            parse_landscape_vpn_block(doc=doc)
        self.assertIn("kind", str(ctx.exception))
        return

    def test_missing_required_key_raises(self) -> None:
        """
            A provider entry missing ``credential_ref`` raises.
        """
        doc = _tailscale_doc()
        del doc["vpn"]["providers"][0]["credential_ref"]
        with self.assertRaises(LandscapeConfigError):
            parse_landscape_vpn_block(doc=doc)
        return

    def test_invalid_default_plane_raises(self) -> None:
        """
            An invalid ``default_plane`` raises.
        """
        doc = _tailscale_doc()
        doc["vpn"]["default_plane"] = "MARS"
        with self.assertRaises(LandscapeConfigError):
            parse_landscape_vpn_block(doc=doc)
        return

    def test_twingate_missing_network_slug_raises(self) -> None:
        """
            A twingate provider without ``network_slug`` is rejected.
        """
        doc = _tailscale_doc()
        doc["vpn"]["providers"][0] = {
            "name": "corp-tg",
            "kind": "twingate",
            "credential_ref": "twingate:corp",
        }
        with self.assertRaises(LandscapeConfigError):
            parse_landscape_vpn_block(doc=doc)
        return


class UnknownKeyTolerance(unittest.TestCase):
    """
        Forward-compatibility surface — unknown leaf keys warn only.
    """

    def test_unknown_key_emits_warning_not_error(self) -> None:
        """
            An unknown root ``vpn:`` key produces only a warning.
        """
        doc = _tailscale_doc()
        doc["vpn"]["future_field"] = 42
        diagnostics = validate_landscape_vpn_block(doc=doc)
        warnings = warnings_from(diagnostics=diagnostics)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].path, "vpn.future_field")
        return

    def test_unknown_provider_key_emits_warning(self) -> None:
        """
            An unknown leaf key under a provider entry produces only a
            warning.
        """
        doc = _tailscale_doc()
        doc["vpn"]["providers"][0]["someday"] = True
        diagnostics = validate_landscape_vpn_block(doc=doc)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        warnings = warnings_from(diagnostics=diagnostics)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("someday", warnings[0].path)
        return


class DeviceOverrideTests(unittest.TestCase):
    """
        Per-device ``vpn:`` override handling.
    """

    def test_device_references_unknown_provider_errors(self) -> None:
        """
            A device referencing a non-existent provider raises.
        """
        doc = _tailscale_doc()
        doc["devices"].append({
            "name": "db01",
            "vpn": {"provider": "ghost", "managed": True},
        })
        with self.assertRaises(LandscapeConfigError):
            parse_landscape_vpn_block(doc=doc)
        return

    def test_device_valid_override_no_errors(self) -> None:
        """
            A device referencing a declared provider validates clean.
        """
        doc = _tailscale_doc()
        doc["devices"].append({
            "name": "db01",
            "vpn": {
                "provider": "corp-tailnet",
                "managed": True,
                "preferred_plane": "OVERLAY",
            },
        })
        diagnostics = validate_landscape_vpn_block(doc=doc)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        self.assertEqual(errors, [])
        return

    def test_device_invalid_preferred_plane_errors(self) -> None:
        """
            An invalid per-device ``preferred_plane`` is an error.
        """
        doc = _tailscale_doc()
        doc["devices"].append({
            "name": "db01",
            "vpn": {
                "provider": "corp-tailnet",
                "preferred_plane": "MARS",
            },
        })
        diagnostics = validate_landscape_vpn_block(doc=doc)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        self.assertEqual(len(errors), 1)
        self.assertIn("preferred_plane", errors[0].path)
        return

    def test_duplicate_provider_name_errors(self) -> None:
        """
            Regression for the audit duplicate-provider-name finding: two
            providers declaring the same ``name`` produce a SEVERITY_ERROR.
        """
        doc = _tailscale_doc()
        doc["vpn"]["providers"].append({
            "name": "corp-tailnet",
            "kind": "twingate",
            "credential_ref": "twingate:corp",
            "network_slug": "corp-net",
        })
        diagnostics = validate_landscape_vpn_block(doc=doc)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        duplicate_errors = [d for d in errors if "duplicate" in d.message]
        self.assertEqual(len(duplicate_errors), 1)
        return

    def test_advertise_tags_non_string_element_errors(self) -> None:
        """
            Regression for the audit advertise_tags element-validation
            finding: a non-string element in ``vpn.advertise_tags`` is an
            error rather than being silently accepted.
        """
        doc = _tailscale_doc()
        doc["devices"].append({
            "name": "db01",
            "vpn": {
                "provider": "corp-tailnet",
                "advertise_tags": ["tag:db", 7, ""],
            },
        })
        diagnostics = validate_landscape_vpn_block(doc=doc)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        tag_errors = [d for d in errors if "advertise_tags[" in d.path]
        self.assertEqual(len(tag_errors), 2)
        return

    def test_apod_section_devices_validated(self) -> None:
        """
            Device entries under ``apod.<section>`` are validated the
            same way as top-level ``devices:`` entries.
        """
        doc: Dict[str, Any] = {
            "vpn": {
                "providers": [
                    {
                        "name": "corp-tg",
                        "kind": "twingate",
                        "credential_ref": "twingate:corp",
                        "network_slug": "corp-net",
                    }
                ],
            },
            "apod": {
                "linux": [
                    {
                        "name": "host01",
                        "vpn": {"provider": "no-such"},
                    }
                ],
            },
        }
        diagnostics = validate_landscape_vpn_block(doc=doc)
        errors = [d for d in diagnostics if d.severity == SEVERITY_ERROR]
        self.assertEqual(len(errors), 1)
        self.assertIn("apod.linux[0].vpn.provider", errors[0].path)
        return


if __name__ == "__main__":
    unittest.main()
