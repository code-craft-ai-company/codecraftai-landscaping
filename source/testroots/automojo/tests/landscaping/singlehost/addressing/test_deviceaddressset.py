"""
    .. module:: test_deviceaddressset
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Example-based tests for the :class:`DeviceAddressSet`
                   class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import unittest

from automojo.interfaces.addressplane import AddressPlane, IDeviceAddressSet
from automojo.landscaping.addressing.deviceaddressset import DeviceAddressSet


class DeviceAddressSetTests(unittest.TestCase):
    """
        Example-based tests covering construction, accessors, setters,
        resolution, and immutable mutation helpers on
        :class:`DeviceAddressSet`.
    """

    def test_constructor_empty(self) -> None:
        """
            An empty constructor yields a set with no populated planes.
        """
        addr_set = DeviceAddressSet()

        self.assertIsNone(addr_set.public())
        self.assertIsNone(addr_set.private())
        self.assertIsNone(addr_set.overlay())
        self.assertEqual(addr_set.planes(), [])

        return

    def test_isinstance_protocol(self) -> None:
        """
            A :class:`DeviceAddressSet` satisfies the
            :class:`IDeviceAddressSet` protocol.
        """
        addr_set = DeviceAddressSet()
        check = isinstance(addr_set, IDeviceAddressSet)
        self.assertTrue(check)
        return

    def test_constructor_populates_planes(self) -> None:
        """
            Constructor arguments populate each plane.
        """
        overlay_map = {"tailscale": "100.64.0.5"}
        addr_set = DeviceAddressSet(public="1.2.3.4", private="10.0.0.5",
                                    overlay=overlay_map)

        self.assertEqual(addr_set.public(), "1.2.3.4")
        self.assertEqual(addr_set.private(), "10.0.0.5")
        self.assertEqual(addr_set.overlay(), "100.64.0.5")
        self.assertEqual(addr_set.overlay(provider="tailscale"), "100.64.0.5")

        return

    def test_empty_string_filtered(self) -> None:
        """
            Empty-string addresses are filtered to ``None`` by accessors.
        """
        addr_set = DeviceAddressSet(public="", private="", overlay={"x": ""})

        self.assertIsNone(addr_set.public())
        self.assertIsNone(addr_set.private())
        self.assertIsNone(addr_set.overlay())
        self.assertIsNone(addr_set.overlay(provider="x"))

        return

    def test_setters_round_trip(self) -> None:
        """
            Setters store values that the accessors return.
        """
        addr_set = DeviceAddressSet()
        addr_set.set_public(address="1.2.3.4")
        addr_set.set_private(address="10.0.0.5")
        addr_set.set_overlay(provider="tailscale", address="100.64.0.5")

        self.assertEqual(addr_set.public(), "1.2.3.4")
        self.assertEqual(addr_set.private(), "10.0.0.5")
        self.assertEqual(addr_set.overlay(provider="tailscale"), "100.64.0.5")

        return

    def test_address_for_each_plane(self) -> None:
        """
            ``address_for`` returns the per-plane value.
        """
        addr_set = DeviceAddressSet(public="p", private="q",
                                    overlay={"a": "r"})

        self.assertEqual(addr_set.address_for(plane=AddressPlane.PUBLIC), "p")
        self.assertEqual(addr_set.address_for(plane=AddressPlane.PRIVATE), "q")
        self.assertEqual(addr_set.address_for(plane=AddressPlane.OVERLAY), "r")

        return

    def test_has_matches_address_for(self) -> None:
        """
            ``has`` returns ``True`` exactly when ``address_for`` would
            return non-``None``.
        """
        addr_set = DeviceAddressSet(public="p")

        self.assertTrue(addr_set.has(plane=AddressPlane.PUBLIC))
        self.assertFalse(addr_set.has(plane=AddressPlane.PRIVATE))
        self.assertFalse(addr_set.has(plane=AddressPlane.OVERLAY))

        return

    def test_planes_ordered(self) -> None:
        """
            ``planes`` lists populated planes in ascending ordinal order.
        """
        addr_set = DeviceAddressSet(private="q", overlay={"a": "r"})

        expected = [AddressPlane.PRIVATE, AddressPlane.OVERLAY]
        self.assertEqual(addr_set.planes(), expected)
        self.assertEqual(addr_set.present_planes(), expected)

        return

    def test_overlay_provider_none_first_inserted(self) -> None:
        """
            ``overlay(provider=None)`` returns the first-inserted entry.
        """
        addr_set = DeviceAddressSet(overlay={"first": "1.1.1.1",
                                             "second": "2.2.2.2"})

        first = addr_set.overlay()
        self.assertEqual(first, "1.1.1.1")

        return

    def test_resolve_uses_preferred_plane(self) -> None:
        """
            ``resolve`` returns the preferred plane's address when present.
        """
        addr_set = DeviceAddressSet(public="p", private="q")

        result = addr_set.resolve(plane=AddressPlane.PRIVATE)
        self.assertEqual(result, "q")

        return

    def test_resolve_walks_fallbacks(self) -> None:
        """
            ``resolve`` walks the fallback list in order.
        """
        addr_set = DeviceAddressSet(public="p")

        result = addr_set.resolve(plane=AddressPlane.OVERLAY,
                                  fallback_planes=[AddressPlane.PRIVATE,
                                                   AddressPlane.PUBLIC])
        self.assertEqual(result, "p")

        return

    def test_resolve_returns_none_when_nothing_present(self) -> None:
        """
            ``resolve`` returns ``None`` when no attempted plane is
            populated.
        """
        addr_set = DeviceAddressSet()

        result = addr_set.resolve(plane=AddressPlane.PUBLIC,
                                  fallback_planes=[AddressPlane.PRIVATE])
        self.assertIsNone(result)

        return

    def test_with_address_immutable(self) -> None:
        """
            ``with_address`` returns a new instance and leaves the
            original unchanged.
        """
        original = DeviceAddressSet(public="orig")
        updated = original.with_address(plane=AddressPlane.PRIVATE,
                                        address="new")

        self.assertIsNot(updated, original)
        self.assertIsNone(original.private())
        self.assertEqual(updated.private(), "new")
        self.assertEqual(updated.public(), "orig")

        return

    def test_with_address_overlay(self) -> None:
        """
            ``with_address`` for the OVERLAY plane uses the supplied
            provider.
        """
        original = DeviceAddressSet()
        updated = original.with_address(plane=AddressPlane.OVERLAY,
                                        address="100.64.0.5",
                                        provider="tailscale")

        self.assertEqual(updated.overlay(provider="tailscale"),
                         "100.64.0.5")
        self.assertEqual(len(original.planes()), 0)

        return

    def test_preferred_address_first_present(self) -> None:
        """
            ``preferred_address`` returns the address of the first
            populated plane in the priority list.
        """
        addr_set = DeviceAddressSet(public="p", private="q")

        result = addr_set.preferred_address(planes=[AddressPlane.OVERLAY,
                                                    AddressPlane.PRIVATE,
                                                    AddressPlane.PUBLIC])
        self.assertEqual(result, "q")

        return

    def test_preferred_address_raises_when_none_present(self) -> None:
        """
            ``preferred_address`` raises ``LookupError`` when no plane
            in the request set is populated.
        """
        addr_set = DeviceAddressSet()

        with self.assertRaises(LookupError):
            _ = addr_set.preferred_address(planes=[AddressPlane.PUBLIC,
                                                   AddressPlane.PRIVATE])

        return


if __name__ == "__main__":
    unittest.main()
