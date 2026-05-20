"""
    .. module:: test_landscapedevice_vpn_overrides
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests verifying per-device ``vpn:`` override
                   resolution on :class:`LandscapeDevice`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import unittest
from types import SimpleNamespace
from typing import Any, Dict, Optional

from hypothesis import given, strategies as st

from automojo.interfaces.addressplane import AddressPlane
from automojo.landscaping.addressing.deviceaddressset import DeviceAddressSet
from automojo.landscaping.landscapedevice import LandscapeDevice


def _stub_landscape(*, vpn_default_plane: Optional[Any] = None) -> SimpleNamespace:
    """
        Build a minimal landscape stand-in exposing the attributes the
        :class:`LandscapeDevice` plane resolver inspects.

        :param vpn_default_plane: Optional landscape-level plane.

        :returns: A namespace usable in place of a real Landscape.
    """
    rtnval = SimpleNamespace()
    if vpn_default_plane is not None:
        rtnval.vpn_default_plane = vpn_default_plane
    return rtnval


def _resolve(*, device_config: Dict[str, Any],
             vpn_default_plane: Optional[Any] = None) -> AddressPlane:
    """
        Run only :meth:`LandscapeDevice._determine_preferred_plane`
        against a stub landscape.

        :param device_config: The device's config dictionary.
        :param vpn_default_plane: Optional landscape default.

        :returns: The resolved :class:`AddressPlane`.
    """
    dev = object.__new__(LandscapeDevice)
    lscape = _stub_landscape(vpn_default_plane=vpn_default_plane)
    rtnval = dev._determine_preferred_plane(lscape=lscape,
                                            device_config=device_config)
    return rtnval


class DevicePreferredPlaneResolutionTests(unittest.TestCase):
    """
        Documented precedence: device vpn override > device top-level
        ``preferred_plane`` > landscape default > PUBLIC.
    """

    def test_default_public_when_nothing_configured(self) -> None:
        """
            No config anywhere yields PUBLIC.
        """
        plane = _resolve(device_config={})
        self.assertEqual(plane, AddressPlane.PUBLIC)
        return

    def test_landscape_default_used_when_device_silent(self) -> None:
        """
            Landscape default propagates when device is silent.
        """
        plane = _resolve(device_config={},
                         vpn_default_plane=AddressPlane.OVERLAY)
        self.assertEqual(plane, AddressPlane.OVERLAY)
        return

    def test_device_vpn_override_wins_over_landscape_default(self) -> None:
        """
            Per-device ``vpn.preferred_plane=OVERLAY`` wins over
            landscape default ``PUBLIC``.
        """
        dev_cfg = {"vpn": {"preferred_plane": "OVERLAY"}}
        plane = _resolve(device_config=dev_cfg,
                         vpn_default_plane=AddressPlane.PUBLIC)
        self.assertEqual(plane, AddressPlane.OVERLAY)
        return

    def test_device_top_level_preferred_plane_wins(self) -> None:
        """
            Legacy top-level ``preferred_plane`` is still honoured.
        """
        dev_cfg = {"preferred_plane": "PRIVATE"}
        plane = _resolve(device_config=dev_cfg,
                         vpn_default_plane=AddressPlane.PUBLIC)
        self.assertEqual(plane, AddressPlane.PRIVATE)
        return

    def test_legacy_preferred_plane_outranks_vpn_block(self) -> None:
        """
            When both are set, the top-level legacy field is taken first
            (consistent with the existing _determine_preferred_plane
            order); the test exists to lock the precedence in.
        """
        dev_cfg = {
            "preferred_plane": "PRIVATE",
            "vpn": {"preferred_plane": "OVERLAY"},
        }
        plane = _resolve(device_config=dev_cfg)
        self.assertEqual(plane, AddressPlane.PRIVATE)
        return


class DeviceVpnOverrideAccessorTests(unittest.TestCase):
    """
        ``vpn_provider`` / ``vpn_managed`` / ``vpn_advertise_tags``
        accessor behaviour.
    """

    def _build(self, *, device_config: Dict[str, Any]) -> LandscapeDevice:
        """
            Build a bare-bones device for accessor testing.

            :param device_config: Device config dictionary.

            :returns: A minimally initialised :class:`LandscapeDevice`.
        """
        dev = object.__new__(LandscapeDevice)
        dev._vpn_provider = None
        dev._vpn_managed = False
        dev._vpn_advertise_tags = []
        dev._initialize_vpn_overrides(device_config=device_config)
        rtnval = dev
        return rtnval

    def test_no_vpn_block_yields_defaults(self) -> None:
        """
            Without a vpn block, accessors return defaults.
        """
        dev = self._build(device_config={})
        self.assertIsNone(dev.vpn_provider)
        self.assertEqual(dev.vpn_managed, False)
        self.assertEqual(dev.vpn_advertise_tags, [])
        return

    def test_vpn_block_populates_accessors(self) -> None:
        """
            All three accessors reflect the device's vpn block.
        """
        cfg = {
            "vpn": {
                "provider": "corp-tailnet",
                "managed": True,
                "advertise_tags": ["tag:lab", "tag:db"],
            }
        }
        dev = self._build(device_config=cfg)
        self.assertEqual(dev.vpn_provider, "corp-tailnet")
        self.assertEqual(dev.vpn_managed, True)
        self.assertEqual(dev.vpn_advertise_tags, ["tag:lab", "tag:db"])
        return

    def test_advertise_tags_returned_as_copy(self) -> None:
        """
            Mutating the returned list does not affect the device.
        """
        cfg = {
            "vpn": {"provider": "x", "advertise_tags": ["a"]}
        }
        dev = self._build(device_config=cfg)
        view = dev.vpn_advertise_tags
        view.append("b")
        self.assertEqual(dev.vpn_advertise_tags, ["a"])
        return


# ---------------------------------------------------------------------------
# Property-based test
# ---------------------------------------------------------------------------

_PLANE_NAMES = ["PUBLIC", "PRIVATE", "OVERLAY"]

_plane_or_none = st.one_of(st.none(), st.sampled_from(_PLANE_NAMES))


@st.composite
def _config_pairs(draw):
    """
        Strategy producing ``(device_config, landscape_default)`` pairs.
    """
    landscape_default_name = draw(_plane_or_none)
    device_vpn_plane = draw(_plane_or_none)

    device_config: Dict[str, Any] = {}
    if device_vpn_plane is not None:
        device_config["vpn"] = {"preferred_plane": device_vpn_plane}

    landscape_default = None
    if landscape_default_name is not None:
        landscape_default = AddressPlane[landscape_default_name]

    return device_config, device_vpn_plane, landscape_default


class PreferredPlanePrecedenceProperty(unittest.TestCase):
    """
        Hypothesis-driven property over the documented precedence rule.
    """

    @given(_config_pairs())
    def test_precedence_rule(self, params) -> None:
        """
            For any combination of (landscape default × per-device
            override) the resolver follows the documented precedence:
            device > landscape > PUBLIC.
        """
        device_config, device_vpn_plane, landscape_default = params

        resolved = _resolve(device_config=device_config,
                            vpn_default_plane=landscape_default)

        if device_vpn_plane is not None:
            expected = AddressPlane[device_vpn_plane]
        elif landscape_default is not None:
            expected = landscape_default
        else:
            expected = AddressPlane.PUBLIC

        self.assertEqual(resolved, expected)
        return


if __name__ == "__main__":
    unittest.main()
