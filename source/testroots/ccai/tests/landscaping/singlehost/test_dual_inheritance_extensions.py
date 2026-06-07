"""
    Tests for the dual-inheritance protocol+control extensions.

    The classes ``DliPowerControlExtension`` and ``TcpSerialProtocolExtension``
    inherit from BOTH :class:`ProtocolExtension` (the device-side surface) and
    :class:`ControlExtension` (the service-side surface).  After the sixth-pass
    audit fix, their ``initialize`` methods seed both sets of bookkeeping
    fields so accessors on either surface resolve correctly.

    These tests exercise that contract using a minimal stand-in dual class that
    avoids the heavy third-party dependencies (``DliPowerOutletControl``,
    ``TcpSerialAgent``) that would otherwise be pulled in.
"""

import weakref

from ccai.testbase import verification

from ccai.landscaping.extensions.protocol.protocolextension import ProtocolExtension
from ccai.landscaping.extensions.control.controlextension import ControlExtension


class _DualSurfaceExtension(ProtocolExtension, ControlExtension):
    """
        Minimal stand-in mirroring the dual-inheritance shape of the real
        ``DliPowerControlExtension`` and ``TcpSerialProtocolExtension``
        classes, without their third-party-library superclasses.
    """

    def __init__(self) -> None:
        ProtocolExtension.__init__(self)
        ControlExtension.__init__(self)
        return

    def initialize(self, coord_ref: weakref.ReferenceType,
                   basedevice_ref: weakref.ReferenceType, extid: str,
                   location: str, configinfo: dict, **kwargs) -> None:
        # Mirror the production shape: seed both surfaces.
        ProtocolExtension.initialize(self, coord_ref, basedevice_ref, extid, location, configinfo, **kwargs)
        ControlExtension.initialize(self, coord_ref, basedevice_ref, extid, configinfo)
        return


class _Coordinator:
    """Stand-in coordinator-and-service object held by weak reference."""


class _Device:
    """Stand-in landscape device held by weak reference."""


def test_pre_init_protocol_surface_is_none_safe() -> None:
    """
        Before :meth:`initialize`, the :class:`ProtocolExtension` accessors
        return ``None`` (not crash).
    """
    ext = _DualSurfaceExtension()
    verification.assert_equal(ext.coordinator, None)
    verification.assert_equal(ext.extends, None)
    return


def test_pre_init_control_surface_is_none_safe() -> None:
    """
        Before :meth:`initialize`, the :class:`ControlExtension` accessors
        return ``None`` (regression for the audit fix that made these
        properties None-safe).
    """
    ext = _DualSurfaceExtension()
    verification.assert_equal(ext.service, None)
    verification.assert_equal(ext.control_id, None)
    verification.assert_equal(ext.control_info, None)
    return


def test_dual_initialize_seeds_protocol_surface() -> None:
    """
        After :meth:`initialize`, the protocol-side accessors resolve to
        the supplied references.
    """
    coord = _Coordinator()
    dev = _Device()
    info = {"outlet": 3}
    ext = _DualSurfaceExtension()
    ext.initialize(
        weakref.ref(coord),
        weakref.ref(dev),
        "power",
        "10.0.0.1",
        info,
    )
    verification.assert_equal(ext.coordinator, coord)
    verification.assert_equal(ext.extends, dev)
    return


def test_dual_initialize_seeds_control_surface() -> None:
    """
        After :meth:`initialize`, the control-side accessors resolve to the
        supplied references — this is the regression test for the bug
        where dual-inheritance ``initialize`` only called the protocol
        side and left ``service`` / ``control_id`` / ``control_info`` as
        ``None``.
    """
    coord = _Coordinator()
    dev = _Device()
    info = {"outlet": 3}
    ext = _DualSurfaceExtension()
    ext.initialize(
        weakref.ref(coord),
        weakref.ref(dev),
        "power",
        "10.0.0.1",
        info,
    )
    verification.assert_equal(ext.service, coord)
    verification.assert_equal(ext.control_id, "power")
    verification.assert_equal(ext.control_info, info)
    return


def test_dual_initialize_supports_kwargs_forwarding() -> None:
    """
        The signature accepts ``**kwargs`` (per the earlier kwargs-widening
        fix) and forwards them to :meth:`ProtocolExtension.initialize`.
    """
    coord = _Coordinator()
    dev = _Device()
    ext = _DualSurfaceExtension()
    # Should not raise even with unexpected keyword arguments.
    ext.initialize(
        weakref.ref(coord),
        weakref.ref(dev),
        "serial",
        "host:9000",
        {"baud": 115200},
        custom_flag=True,
        another_extra="value",
    )
    verification.assert_equal(ext.coordinator, coord)
    verification.assert_equal(ext.service, coord)
    verification.assert_equal(ext.control_id, "serial")
    return


def test_update_extends_ref_updates_both_surfaces() -> None:
    """
        Because both surfaces share the underlying ``_extends_ref``
        attribute, calling :meth:`update_extends_ref` (provided by
        :class:`ProtocolExtension` via inheritance) keeps both surfaces in
        sync.
    """
    coord = _Coordinator()
    dev1 = _Device()
    dev2 = _Device()
    ext = _DualSurfaceExtension()
    ext.initialize(
        weakref.ref(coord),
        weakref.ref(dev1),
        "power",
        "10.0.0.1",
        {"outlet": 3},
    )
    verification.assert_equal(ext.extends, dev1)
    # Swap the device.
    ext.update_extends_ref(weakref.ref(dev2))
    verification.assert_equal(ext.extends, dev2)
    return
