"""
    .. module:: test_vpncoordinatorcoupling_registration
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests that :class:`VPNCoordinatorCoupling` registers
                   its coupling kind with the landscape coordinator
                   factory and is discoverable through the normal
                   factory path.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import unittest

from ccai.errors.exceptions import ConfigurationError

from ccai.landscaping.coupling.vpncoordinatorcoupling import (
    VPNCoordinatorCoupling,
    VPN_COORDINATOR_COUPLING_KIND,
    coupling_type_for_kind,
    is_coupling_kind_registered,
)


class VPNCoordinatorCouplingRegistrationTests(unittest.TestCase):
    """
        Tests for the coupling-kind registration surface.
    """

    def test_register_makes_kind_discoverable(self) -> None:
        VPNCoordinatorCoupling.register()
        self.assertTrue(
            is_coupling_kind_registered(kind=VPN_COORDINATOR_COUPLING_KIND))
        return

    def test_coupling_type_for_kind_returns_coupling_class(self) -> None:
        VPNCoordinatorCoupling.register()
        resolved = coupling_type_for_kind(kind=VPN_COORDINATOR_COUPLING_KIND)
        self.assertIs(resolved, VPNCoordinatorCoupling)
        return

    def test_coupling_type_for_unknown_kind_raises(self) -> None:
        with self.assertRaises(ConfigurationError):
            coupling_type_for_kind(kind="not-a-registered-kind")
        return

    def test_factories_module_registers_vpn_coupling_kind(self) -> None:
        # The landscape factories module is the normal factory path;
        # its source must invoke ``VPNCoordinatorCoupling.register()`` so
        # a landscape with a ``vpn:`` block resolves the coupling class.
        # The module is not imported here because it requires
        # application-persona setup; the registration statement is
        # asserted at the source level instead.
        import importlib.util

        spec = importlib.util.find_spec("ccai.landscaping.factories")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.origin)

        with open(spec.origin, "r", encoding="utf-8") as factories_file:
            source_text = factories_file.read()

        self.assertIn("VPNCoordinatorCoupling.register()", source_text)
        return

    def test_vpn_kind_key_is_vpn(self) -> None:
        self.assertEqual(VPN_COORDINATOR_COUPLING_KIND, "vpn")
        return


if __name__ == "__main__":
    unittest.main()
