"""
    .. module:: test_vpncoordinatorcoupling_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hypothesis property tests for
                   :class:`VPNCoordinatorCoupling`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

from __future__ import annotations


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import unittest

from typing import Dict, List, Optional

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.interfaces.ivpncontrolplane import VPNDeviceRecord
from ccai.landscaping.coupling.aspectslandscapecoupling import (
    AspectsLandscapeCoupling,
)
from ccai.landscaping.coupling.vpncoordinatorcoupling import (
    VPNCoordinatorCoupling,
)

from ccai.tests.landscaping.singlehost.coupling.test_vpncoordinatorcoupling import (
    FakeDevice,
    make_control_plane,
)


hostname_alphabet = st.text(alphabet="abcdefghijklmnop", min_size=1, max_size=8)
ip_octet = st.integers(min_value=0, max_value=255)


def ip_strategy() -> st.SearchStrategy[str]:
    """
        Build a strategy that emits dotted-quad IP-address strings.
    """
    rtnval = st.tuples(ip_octet, ip_octet, ip_octet, ip_octet).map(
        lambda parts: "{}.{}.{}.{}".format(parts[0], parts[1], parts[2], parts[3])
    )
    return rtnval


def record_strategy() -> st.SearchStrategy[VPNDeviceRecord]:
    """
        Build a strategy that emits :class:`VPNDeviceRecord` instances
        with non-empty hostnames and an overlay address.
    """
    rtnval = st.builds(
        VPNDeviceRecord,
        device_id=st.text(alphabet="0123456789abcdef", min_size=4, max_size=8),
        hostname=hostname_alphabet,
        overlay_address=ip_strategy(),
    )
    return rtnval


def records_strategy() -> st.SearchStrategy[List[VPNDeviceRecord]]:
    """
        Build a strategy that emits a unique-hostname list of records.
    """
    rtnval = st.lists(record_strategy(), min_size=0, max_size=8,
                      unique_by=lambda r: r.hostname.lower())
    return rtnval


def devices_strategy() -> st.SearchStrategy[List[FakeDevice]]:
    """
        Build a strategy that emits a list of :class:`FakeDevice`
        instances with distinct hostnames.
    """
    rtnval = st.lists(hostname_alphabet, min_size=0, max_size=8,
                      unique_by=lambda h: h.lower()).map(
        lambda names: [FakeDevice(hostname=name) for name in names]
    )
    return rtnval


def snapshot_overlay(devices: List[FakeDevice],
                     provider: str) -> Dict[str, Optional[str]]:
    """
        Capture a hostname -> overlay-address snapshot for ``devices``.
    """
    snap: Dict[str, Optional[str]] = {}
    for device in devices:
        host = device.hostname
        if host is None:
            continue
        snap[host.lower()] = device.addresses.overlay(provider=provider)
    rtnval = snap
    return rtnval


class VPNCoordinatorCouplingProperties(unittest.TestCase):
    """
        Property tests covering idempotency and order-independence.
    """

    @given(records=records_strategy(), devices=devices_strategy(), constraints={"max_examples": 50})
    def test_couple_is_idempotent(self,
                                  records: List[VPNDeviceRecord],
                                  devices: List[FakeDevice]) -> None:
        cp = make_control_plane(records)
        coupling = VPNCoordinatorCoupling(provider="tailscale",
                                          control_plane=cp)
        aspects = AspectsLandscapeCoupling(raise_on_ambiguous=False)

        coupling.couple(devices=devices, aspects=aspects)
        first_snap = snapshot_overlay(devices, "tailscale")

        second = coupling.couple(devices=devices, aspects=aspects)
        second_snap = snapshot_overlay(devices, "tailscale")

        self.assertEqual(second.updated, 0)
        self.assertEqual(first_snap, second_snap)
        return

    @given(
    constraints={"max_examples": 50},records=records_strategy(), devices=devices_strategy(),
           seed=st.integers(min_value=0, max_value=10000))
    def test_couple_is_order_independent(self,
                                         records: List[VPNDeviceRecord],
                                         devices: List[FakeDevice],
                                         seed: int) -> None:
        # Build two devices lists carrying the same hostnames so the
        # final overlay state may be compared by hostname.
        hostnames = [d.hostname for d in devices if d.hostname is not None]
        devices_a = [FakeDevice(hostname=h) for h in hostnames]
        # Reverse to vary iteration order.
        devices_b = [FakeDevice(hostname=h) for h in reversed(hostnames)]
        _ = seed

        cp_a = make_control_plane(records)
        coupling_a = VPNCoordinatorCoupling(provider="tailscale",
                                            control_plane=cp_a)
        cp_b = make_control_plane(list(reversed(records)))
        coupling_b = VPNCoordinatorCoupling(provider="tailscale",
                                            control_plane=cp_b)

        aspects = AspectsLandscapeCoupling(raise_on_ambiguous=False)
        coupling_a.couple(devices=devices_a, aspects=aspects)
        coupling_b.couple(devices=devices_b, aspects=aspects)

        snap_a = snapshot_overlay(devices_a, "tailscale")
        snap_b = snapshot_overlay(devices_b, "tailscale")

        self.assertEqual(snap_a, snap_b)
        return


if __name__ == "__main__":
    unittest.main()
