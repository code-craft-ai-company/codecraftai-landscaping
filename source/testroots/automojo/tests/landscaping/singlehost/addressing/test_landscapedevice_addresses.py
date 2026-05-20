"""
    .. module:: test_landscapedevice_addresses
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Integration tests verifying the ``addresses`` /
                   ``preferred_plane`` surface on :class:`LandscapeDevice`
                   and the backward-compatible ``_host`` shim.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import unittest

from automojo.interfaces.addressplane import AddressPlane
from automojo.landscaping.addressing.deviceaddressset import DeviceAddressSet
from automojo.landscaping.landscapedevice import LandscapeDevice


def _build_device(*, host: str = "10.1.2.3",
                  configured_ipaddr: str = "10.1.2.3",
                  preferred_plane: AddressPlane = AddressPlane.PUBLIC) -> LandscapeDevice:
    """
        Build a bare-bones :class:`LandscapeDevice` without going through
        the full ``__init__`` chain (which requires a Landscape and
        Coordinator). This mirrors the pattern used in
        ``test_device_extension_accessors.py``.

        :param host: The ``_host`` to attach.
        :param configured_ipaddr: The configured IP to attach.
        :param preferred_plane: The preferred plane to assign.

        :returns: A minimally initialised :class:`LandscapeDevice`.
    """
    dev = object.__new__(LandscapeDevice)
    dev._host = host
    dev._configured_ipaddr = configured_ipaddr
    dev._address_set = DeviceAddressSet(public=host)
    dev._preferred_plane = preferred_plane
    dev._overlay_warning_emitted = False
    return dev


class LandscapeDeviceAddressesTests(unittest.TestCase):
    """
        Integration tests for the new addressing surface on
        :class:`LandscapeDevice`.
    """

    def test_host_still_readable(self) -> None:
        """
            The legacy ``_host`` attribute is preserved.
        """
        dev = _build_device(host="my-host.example.com")
        self.assertEqual(dev._host, "my-host.example.com")
        return

    def test_addresses_returns_address_set(self) -> None:
        """
            The ``addresses`` property returns a :class:`DeviceAddressSet`.
        """
        dev = _build_device(host="1.2.3.4")
        addr_set = dev.addresses
        self.assertIsInstance(addr_set, DeviceAddressSet)
        self.assertEqual(addr_set.public(), "1.2.3.4")
        return

    def test_preferred_plane_default_public(self) -> None:
        """
            The ``preferred_plane`` property defaults to
            :attr:`AddressPlane.PUBLIC`.
        """
        dev = _build_device()
        self.assertEqual(dev.preferred_plane, AddressPlane.PUBLIC)
        return

    def test_preferred_plane_configurable(self) -> None:
        """
            The ``preferred_plane`` property reflects the configured
            value.
        """
        dev = _build_device(preferred_plane=AddressPlane.OVERLAY)
        self.assertEqual(dev.preferred_plane, AddressPlane.OVERLAY)
        return

    def test_address_set_public_matches_host(self) -> None:
        """
            On construction the address set's PUBLIC slot mirrors the
            legacy ``_host`` value so existing callers see the same
            answer through either path.
        """
        dev = _build_device(host="my-host.example.com")
        public_addr = dev.addresses.address_for(plane=AddressPlane.PUBLIC)
        self.assertEqual(public_addr, dev._host)
        return


if __name__ == "__main__":
    unittest.main()
