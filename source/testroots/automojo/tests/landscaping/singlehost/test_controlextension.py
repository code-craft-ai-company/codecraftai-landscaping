"""
    Tests for the :class:`ControlExtension` base class.

    Locks in the regressions introduced by the sixth-pass audit:

    * ``extends`` and ``service`` properties must return ``None`` rather
      than crash with ``TypeError`` when the extension has not yet been
      bound (the canonical state immediately after ``__init__``) or when
      the underlying weak reference has been collected.
    * ``update_extends_ref`` and ``update_service_ref`` must exist on the
      base class (so pure :class:`ControlExtension` subclasses that do
      not also inherit :class:`ProtocolExtension` can be wired up
      symmetrically).
"""

import gc
import weakref

from automojo.testbase import verification

from automojo.landscaping.extensions.control.controlextension import ControlExtension


class _FakeService:
    """Stand-in for a ServiceBase used only as a weakref target."""


class _FakeDevice:
    """Stand-in for a LandscapeDevice used only as a weakref target."""


def test_extends_property_returns_none_when_unbound() -> None:
    """
        After :meth:`__init__` and before :meth:`initialize`, ``extends``
        must return ``None`` (not raise ``TypeError`` from a ``None`` deref).
    """
    ext = ControlExtension()
    verification.assert_equal(ext.extends, None)
    return


def test_service_property_returns_none_when_unbound() -> None:
    """
        After :meth:`__init__` and before :meth:`initialize`, ``service``
        must return ``None`` (not raise).
    """
    ext = ControlExtension()
    verification.assert_equal(ext.service, None)
    return


def test_control_id_and_control_info_are_none_when_unbound() -> None:
    """
        Both attribute accessors return ``None`` until ``initialize`` runs.
    """
    ext = ControlExtension()
    verification.assert_equal(ext.control_id, None)
    verification.assert_equal(ext.control_info, None)
    return


def test_initialize_seeds_all_four_fields() -> None:
    """
        :meth:`initialize` populates ``service_ref`` / ``extends_ref`` /
        ``control_id`` / ``control_info``.
    """
    ext = ControlExtension()
    svc = _FakeService()
    dev = _FakeDevice()
    info = {"server": "host-1", "outlet": 3}
    ext.initialize(
        service_ref=weakref.ref(svc),
        extends_ref=weakref.ref(dev),
        control_id="power-3",
        control_info=info,
    )
    verification.assert_equal(ext.service, svc)
    verification.assert_equal(ext.extends, dev)
    verification.assert_equal(ext.control_id, "power-3")
    verification.assert_equal(ext.control_info, info)
    return


def test_update_extends_ref_attaches_device_after_construction() -> None:
    """
        :meth:`update_extends_ref` lets a coordinator pre-create a
        control extension and bind it to a device later.  The base class
        must offer this method directly so pure ControlExtension
        subclasses (no ProtocolExtension mixin) work uniformly.
    """
    ext = ControlExtension()
    dev = _FakeDevice()
    ext.update_extends_ref(extends_ref=weakref.ref(dev))
    verification.assert_equal(ext.extends, dev)
    return


def test_update_service_ref_attaches_service_after_construction() -> None:
    """
        Symmetric counterpart of ``update_extends_ref`` — binds the
        owning service after the extension was already created.
    """
    ext = ControlExtension()
    svc = _FakeService()
    ext.update_service_ref(service_ref=weakref.ref(svc))
    verification.assert_equal(ext.service, svc)
    return


def test_extends_returns_none_after_referent_collected() -> None:
    """
        Once the underlying device has been garbage-collected, the
        ``extends`` property must return ``None`` rather than crash.
    """
    ext = ControlExtension()
    dev = _FakeDevice()
    ext.update_extends_ref(extends_ref=weakref.ref(dev))
    verification.assert_equal(ext.extends, dev)
    del dev
    gc.collect()
    verification.assert_equal(ext.extends, None)
    return


def test_service_returns_none_after_referent_collected() -> None:
    """
        Once the underlying service has been garbage-collected, the
        ``service`` property must return ``None`` rather than crash.
    """
    ext = ControlExtension()
    svc = _FakeService()
    ext.update_service_ref(service_ref=weakref.ref(svc))
    verification.assert_equal(ext.service, svc)
    del svc
    gc.collect()
    verification.assert_equal(ext.service, None)
    return
