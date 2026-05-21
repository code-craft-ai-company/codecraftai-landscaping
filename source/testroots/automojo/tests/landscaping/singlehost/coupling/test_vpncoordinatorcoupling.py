"""
    .. module:: test_vpncoordinatorcoupling
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Example-based tests for
                   :class:`VPNCoordinatorCoupling`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import unittest

from typing import Any, List, Optional
from unittest.mock import MagicMock

from automojo.errors.exceptions import ConfigurationError
from automojo.interfaces.ivpnclient import IVPNClient
from automojo.interfaces.ivpncontrolplane import IVPNControlPlane, VPNDeviceRecord

from automojo.landscaping.addressing.deviceaddressset import DeviceAddressSet
from automojo.landscaping.coupling.aspectslandscapecoupling import (
    AspectsLandscapeCoupling,
    DEFAULT_LANDSCAPE_COUPLING_ASPECTS,
)
from automojo.landscaping.coupling.exceptions import (
    VPNCoordinatorAmbiguousMatchError,
)
from automojo.landscaping.coupling.vpncoordinatorcoupling import (
    VPNCoordinatorCoupling,
)


class FakeDevice:
    """
        Minimal duck-typed landscape device for coupling tests.
    """

    def __init__(self, *, hostname: Optional[str],
                 tags: Optional[List[str]] = None,
                 managed: bool = False,
                 full_identifier: Optional[str] = None) -> None:
        self._hostname = hostname
        if tags is None:
            self._tags: List[str] = []
        else:
            self._tags = list(tags)
        self._addresses = DeviceAddressSet()
        self._device_config: dict = {}
        if managed:
            self._device_config["vpn"] = {"managed": True}
        if full_identifier is not None:
            self._full_identifier = full_identifier
        else:
            self._full_identifier = hostname if hostname is not None else "device"
        self._vpn_clients: dict = {}
        return

    @property
    def hostname(self) -> Optional[str]:
        rtnval = self._hostname
        return rtnval

    @property
    def tags(self) -> List[str]:
        rtnval = list(self._tags)
        return rtnval

    @property
    def addresses(self) -> DeviceAddressSet:
        rtnval = self._addresses
        return rtnval

    @property
    def device_config(self) -> dict:
        rtnval = self._device_config
        return rtnval

    @property
    def full_identifier(self) -> str:
        rtnval = self._full_identifier
        return rtnval

    def register_vpn_client(self, *, provider: str, client: IVPNClient) -> None:
        self._vpn_clients[provider] = client
        return

    def vpn_client_for(self, *, provider: str) -> Optional[IVPNClient]:
        rtnval = self._vpn_clients.get(provider, None)
        return rtnval


def make_control_plane(records: List[VPNDeviceRecord]) -> MagicMock:
    """
        Build a mock :class:`IVPNControlPlane` that returns ``records``.
    """
    cp = MagicMock(spec=IVPNControlPlane)
    cp.list_devices.return_value = list(records)
    rtnval = cp
    return rtnval


class VPNCoordinatorCouplingTests(unittest.TestCase):
    """
        Example-based tests for :class:`VPNCoordinatorCoupling`.
    """

    def test_couple_hostname_match_attaches_overlay(self) -> None:
        device_a = FakeDevice(hostname="alpha")
        device_b = FakeDevice(hostname="bravo")
        device_c = FakeDevice(hostname="charlie")

        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
            VPNDeviceRecord(device_id="b", hostname="bravo",
                            overlay_address="100.64.0.2"),
            VPNDeviceRecord(device_id="c", hostname="charlie",
                            overlay_address="100.64.0.3"),
        ]
        cp = make_control_plane(records)

        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)

        result = coupling.couple(devices=[device_a, device_b, device_c])

        self.assertEqual(result.updated, 3)
        self.assertEqual(result.unmatched, 0)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(device_a.addresses.overlay(provider="tailscale"),
                         "100.64.0.1")
        self.assertEqual(device_b.addresses.overlay(provider="tailscale"),
                         "100.64.0.2")
        self.assertEqual(device_c.addresses.overlay(provider="tailscale"),
                         "100.64.0.3")
        return

    def test_couple_hostname_match_is_case_insensitive(self) -> None:
        device = FakeDevice(hostname="ALPHA")
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        result = coupling.couple(devices=[device])
        self.assertEqual(result.updated, 1)
        self.assertEqual(device.addresses.overlay(provider="tailscale"),
                         "100.64.0.1")
        return

    def test_couple_tag_match_attaches_overlay(self) -> None:
        device = FakeDevice(hostname="unknown-host", tags=["role:db"])
        records = [
            VPNDeviceRecord(device_id="db1", hostname="db-server-1",
                            overlay_address="100.64.0.5",
                            tags=["role:db"]),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        result = coupling.couple(devices=[device])
        self.assertEqual(result.updated, 1)
        self.assertEqual(device.addresses.overlay(provider="tailscale"),
                         "100.64.0.5")
        return

    def test_couple_tag_match_multiple_raises_when_strict(self) -> None:
        device = FakeDevice(hostname="unknown", tags=["role:db"])
        records = [
            VPNDeviceRecord(device_id="db1", hostname="db1",
                            overlay_address="100.64.0.5",
                            tags=["role:db"]),
            VPNDeviceRecord(device_id="db2", hostname="db2",
                            overlay_address="100.64.0.6",
                            tags=["role:db"]),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)

        with self.assertRaises(VPNCoordinatorAmbiguousMatchError):
            coupling.couple(devices=[device])
        return

    def test_couple_tag_match_multiple_records_when_lenient(self) -> None:
        device = FakeDevice(hostname="unknown", tags=["role:db"])
        records = [
            VPNDeviceRecord(device_id="db1", hostname="db1",
                            overlay_address="100.64.0.5",
                            tags=["role:db"]),
            VPNDeviceRecord(device_id="db2", hostname="db2",
                            overlay_address="100.64.0.6",
                            tags=["role:db"]),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)

        lenient = AspectsLandscapeCoupling(raise_on_ambiguous=False)
        result = coupling.couple(devices=[device], aspects=lenient)

        self.assertEqual(result.unmatched, 1)
        self.assertEqual(len(result.ambiguous_tag_matches), 1)
        self.assertIsNone(device.addresses.overlay(provider="tailscale"))
        return

    def test_couple_hostname_supersedes_tag(self) -> None:
        device = FakeDevice(hostname="alpha", tags=["role:db"])
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
            VPNDeviceRecord(device_id="db1", hostname="db1",
                            overlay_address="100.64.0.5",
                            tags=["role:db"]),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        result = coupling.couple(devices=[device])
        self.assertEqual(result.updated, 1)
        self.assertEqual(device.addresses.overlay(provider="tailscale"),
                         "100.64.0.1")
        return

    def test_couple_unmatched_leaves_overlay_untouched(self) -> None:
        device = FakeDevice(hostname="orphan")
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        result = coupling.couple(devices=[device])
        self.assertEqual(result.unmatched, 1)
        self.assertEqual(result.updated, 0)
        self.assertIsNone(device.addresses.overlay(provider="tailscale"))
        return

    def test_couple_twingate_asymmetry_skips_none_overlay(self) -> None:
        device = FakeDevice(hostname="alpha")
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address=None),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="twingate",
                                          control_plane=cp)
        result = coupling.couple(devices=[device])
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.updated, 0)
        self.assertIsNone(device.addresses.overlay(provider="twingate"))
        return

    def test_recouple_is_idempotent(self) -> None:
        device_a = FakeDevice(hostname="alpha")
        device_b = FakeDevice(hostname="bravo")

        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
            VPNDeviceRecord(device_id="b", hostname="bravo",
                            overlay_address="100.64.0.2"),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)

        first = coupling.couple(devices=[device_a, device_b])
        second = coupling.couple(devices=[device_a, device_b])

        self.assertEqual(first.updated, 2)
        self.assertEqual(second.updated, 0)
        self.assertEqual(second.skipped, 2)
        return

    def test_refresh_is_equivalent_to_couple(self) -> None:
        device = FakeDevice(hostname="alpha")
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)

        first = coupling.couple(devices=[device])
        records[0] = VPNDeviceRecord(device_id="a", hostname="alpha",
                                     overlay_address="100.64.0.99")
        cp.list_devices.return_value = list(records)

        second = coupling.refresh(devices=[device])

        self.assertEqual(first.updated, 1)
        self.assertEqual(second.updated, 1)
        self.assertEqual(device.addresses.overlay(provider="tailscale"),
                         "100.64.0.99")
        return

    def test_decouple_clears_overlay_only(self) -> None:
        device = FakeDevice(hostname="alpha")
        device.addresses.set_public(address="203.0.113.1")
        device.addresses.set_private(address="10.0.0.1")
        device.addresses.set_overlay(provider="tailscale",
                                     address="100.64.0.1")

        cp = make_control_plane([])
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)

        coupling.decouple(devices=[device])

        self.assertIsNone(device.addresses.overlay(provider="tailscale"))
        self.assertEqual(device.addresses.public(), "203.0.113.1")
        self.assertEqual(device.addresses.private(), "10.0.0.1")
        return

    def test_managed_host_without_factory_raises(self) -> None:
        device = FakeDevice(hostname="alpha", managed=True)
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp,
                                          vpn_client_factory=None)
        with self.assertRaises(ConfigurationError):
            coupling.couple(devices=[device])
        return

    def test_managed_host_registers_vpn_client(self) -> None:
        device = FakeDevice(hostname="alpha", managed=True)
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)

        fake_client = MagicMock(spec=IVPNClient)

        def factory(*, device: Any, provider: str) -> IVPNClient:
            _ = device
            _ = provider
            rtnval = fake_client
            return rtnval

        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp,
                                          vpn_client_factory=factory)
        coupling.couple(devices=[device])

        self.assertIs(device.vpn_client_for(provider="tailscale"), fake_client)
        return

    def test_couple_twice_does_not_re_register_managed_client(self) -> None:
        # Regression for audit IL-H4: couple() is documented idempotent, but
        # for managed devices it rebuilt and re-registered the IVPNClient on
        # every call. A second couple() must not invoke the factory again.
        device = FakeDevice(hostname="alpha", managed=True)
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)

        invocations: List[Any] = []

        def factory(*, device: Any, provider: str) -> IVPNClient:
            invocations.append((device, provider))
            rtnval = MagicMock(spec=IVPNClient)
            return rtnval

        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp,
                                          vpn_client_factory=factory)
        coupling.couple(devices=[device])
        first_client = device.vpn_client_for(provider="tailscale")

        coupling.couple(devices=[device])
        second_client = device.vpn_client_for(provider="tailscale")

        self.assertEqual(len(invocations), 1)
        self.assertIs(first_client, second_client)
        return

    def test_managed_host_factory_returning_none_raises(self) -> None:
        device = FakeDevice(hostname="alpha", managed=True)
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)

        def factory(*, device: Any, provider: str) -> Optional[IVPNClient]:
            _ = device
            _ = provider
            rtnval: Optional[IVPNClient] = None
            return rtnval

        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp,
                                          vpn_client_factory=factory)
        with self.assertRaises(ConfigurationError):
            coupling.couple(devices=[device])
        return

    def test_unmanaged_host_does_not_invoke_factory(self) -> None:
        device = FakeDevice(hostname="alpha", managed=False)
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)

        invocations: List[Any] = []

        def factory(*, device: Any, provider: str) -> Optional[IVPNClient]:
            invocations.append((device, provider))
            rtnval: Optional[IVPNClient] = None
            return rtnval

        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp,
                                          vpn_client_factory=factory)
        coupling.couple(devices=[device])
        self.assertEqual(len(invocations), 0)
        return

    def test_couple_with_no_devices_returns_empty_result(self) -> None:
        cp = make_control_plane([])
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        result = coupling.couple(devices=[])
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(result.unmatched, 0)
        self.assertEqual(result.provider, "tailscale")
        return

    def test_default_aspects_singleton_is_used(self) -> None:
        device = FakeDevice(hostname="alpha")
        records = [
            VPNDeviceRecord(device_id="a", hostname="alpha",
                            overlay_address="100.64.0.1"),
        ]
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        coupling.couple(devices=[device])
        call_args = cp.list_devices.call_args
        self.assertIsNotNone(call_args)
        passed_aspects = call_args.kwargs["aspects"]
        self.assertEqual(passed_aspects.completion_timeout,
                         DEFAULT_LANDSCAPE_COUPLING_ASPECTS.timeout_seconds)
        return


if __name__ == "__main__":
    unittest.main()
