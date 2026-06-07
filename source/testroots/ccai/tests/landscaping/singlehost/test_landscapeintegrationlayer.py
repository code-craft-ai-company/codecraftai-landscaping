"""
    Tests for :class:`LandscapeIntegrationLayer` properties and filter methods.

    These tests bypass the full constructor (which requires a fully-bootstrapped
    Landscape) by using ``object.__new__`` and directly seeding only the small
    set of instance attributes that the methods under test touch.

    Coverage focuses on the bug-prone methods called out in the recent five-pass
    audit:

      * The four ``integrated_*`` properties — regression for the
        ``_integrated_*`` attrs being initialised to ``None`` (which caused
        ``.copy()`` inside the properties to ``AttributeError``).
      * ``get_devices`` and ``get_services`` filter combinations — regression
        for the exclude-filter loop bug (missing ``break`` causing duplicate
        appends, plus inverted semantic).
"""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from ccai.testbase import verification

from ccai.landscaping.excludefilters import (
    ExcludeDeviceByName,
    ExcludeServiceByName,
)
from ccai.landscaping.includefilters import (
    IncludeDeviceByName,
    IncludeServiceByName,
)
from ccai.landscaping.landscapedevice import LandscapeDevice
from ccai.landscaping.landscapeservice import LandscapeService
from ccai.landscaping.layers.landscapeintegrationlayer import LandscapeIntegrationLayer


def _build_fake_landscape() -> MagicMock:
    """
        Builds a mock landscape whose ``begin_locked_landscape_scope`` returns
        a context manager that enters/exits cleanly without doing any real work.

        :returns: A ``MagicMock`` standing in for a Landscape object.
    """
    fake_lscape = MagicMock()
    fake_scope = MagicMock()
    fake_scope.__enter__ = MagicMock(return_value=fake_scope)
    fake_scope.__exit__ = MagicMock(return_value=False)
    fake_lscape.begin_locked_landscape_scope.return_value = fake_scope
    return fake_lscape


def _build_integration_layer(
    devices: Optional[Dict[str, LandscapeDevice]] = None,
    services: Optional[Dict[str, LandscapeService]] = None,
    power: Optional[Dict[str, Any]] = None,
    serial: Optional[Dict[str, Any]] = None,
) -> LandscapeIntegrationLayer:
    """
        Builds a minimally-initialised ``LandscapeIntegrationLayer`` that
        bypasses the heavyweight constructor.  Only the attributes exercised
        by properties / filter methods are seeded.

        :param devices: Optional pre-populated integrated devices map.
        :param services: Optional pre-populated integrated services map.
        :param power: Optional pre-populated integrated power map.
        :param serial: Optional pre-populated integrated serial map.

        :returns: A test-ready :class:`LandscapeIntegrationLayer` instance.
    """
    layer = object.__new__(LandscapeIntegrationLayer)

    layer._integrated_devices = devices if devices is not None else {}
    layer._integrated_services = services if services is not None else {}
    layer._integrated_power = power if power is not None else {}
    layer._integrated_serial = serial if serial is not None else {}

    layer._integrated_device_groups = {}
    layer._coordinators_for_devices = {}
    layer._coordinators_for_power = {}
    layer._coordinators_for_serial = {}
    layer._coordinators_for_services = {}
    layer._requested_integration_couplings = {}
    layer._power_request_count = 0
    layer._serial_request_count = 0

    fake_lscape = _build_fake_landscape()
    layer._lscape_ref = lambda: fake_lscape

    return layer


def _build_device(
    name: str = "dev0",
    device_type: str = "router",
    role: str = "primary",
    group: str = "core",
) -> LandscapeDevice:
    """
        Constructs a minimally-initialised :class:`LandscapeDevice`.

        :param name: The device name.
        :param device_type: The device type label.
        :param role: The device role label.
        :param group: The device group label.

        :returns: A bare :class:`LandscapeDevice` suitable for filter exercises.
    """
    device = object.__new__(LandscapeDevice)
    device._device_type = device_type
    device._role = role
    device._group = group
    device._name = name
    return device


def _build_service(name: str = "svc0") -> LandscapeService:
    """
        Constructs a minimally-initialised :class:`LandscapeService`.

        :param name: The service name.

        :returns: A bare :class:`LandscapeService` suitable for filter exercises.
    """
    service = object.__new__(LandscapeService)
    service._name = name
    return service


# ---------------------------------------------------------------------------
# Property tests — regression for the None-init bug (pass 3).
# ---------------------------------------------------------------------------


def test_integrated_devices_returns_empty_dict_when_unpopulated() -> None:
    layer = _build_integration_layer()

    result = layer.integrated_devices

    verification.assert_equal(isinstance(result, dict), True)
    verification.assert_equal(len(result), 0)


def test_integrated_services_returns_empty_dict_when_unpopulated() -> None:
    layer = _build_integration_layer()

    result = layer.integrated_services

    verification.assert_equal(isinstance(result, dict), True)
    verification.assert_equal(len(result), 0)


def test_integrated_power_returns_empty_dict_when_unpopulated() -> None:
    layer = _build_integration_layer()

    result = layer.integrated_power

    verification.assert_equal(isinstance(result, dict), True)
    verification.assert_equal(len(result), 0)


def test_integrated_serial_returns_empty_dict_when_unpopulated() -> None:
    layer = _build_integration_layer()

    result = layer.integrated_serial

    verification.assert_equal(isinstance(result, dict), True)
    verification.assert_equal(len(result), 0)


def test_integrated_devices_returns_copy_of_underlying_state() -> None:
    device_a = _build_device(name="alpha")
    devices = {"alpha": device_a}
    layer = _build_integration_layer(devices=devices)

    result = layer.integrated_devices

    verification.assert_equal(len(result), 1)
    verification.assert_equal("alpha" in result, True)
    is_same_object = result is layer._integrated_devices
    verification.assert_equal(is_same_object, False)


def test_integrated_services_returns_copy_of_underlying_state() -> None:
    service_a = _build_service(name="api")
    services = {"api": service_a}
    layer = _build_integration_layer(services=services)

    result = layer.integrated_services

    verification.assert_equal(len(result), 1)
    verification.assert_equal("api" in result, True)
    is_same_object = result is layer._integrated_services
    verification.assert_equal(is_same_object, False)


def test_integrated_power_returns_copy_of_underlying_state() -> None:
    power_map = {"power-key": object()}
    layer = _build_integration_layer(power=power_map)

    result = layer.integrated_power

    verification.assert_equal(len(result), 1)
    verification.assert_equal("power-key" in result, True)
    is_same_object = result is layer._integrated_power
    verification.assert_equal(is_same_object, False)


def test_integrated_serial_returns_copy_of_underlying_state() -> None:
    serial_map = {"serial-key": object()}
    layer = _build_integration_layer(serial=serial_map)

    result = layer.integrated_serial

    verification.assert_equal(len(result), 1)
    verification.assert_equal("serial-key" in result, True)
    is_same_object = result is layer._integrated_serial
    verification.assert_equal(is_same_object, False)


# ---------------------------------------------------------------------------
# get_devices() — public contract + regression for exclude bug.
# ---------------------------------------------------------------------------


def test_get_devices_with_no_filters_returns_all_devices() -> None:
    device_a = _build_device(name="A")
    device_b = _build_device(name="B")
    device_c = _build_device(name="C")
    devices = {"A": device_a, "B": device_b, "C": device_c}
    layer = _build_integration_layer(devices=devices)

    result = layer.get_devices()

    result_names = sorted([dev._name for dev in result])
    verification.assert_equal(result_names, ["A", "B", "C"])


def test_get_devices_with_include_filter_returns_only_matching() -> None:
    device_a = _build_device(name="A")
    device_b = _build_device(name="B")
    device_c = _build_device(name="C")
    devices = {"A": device_a, "B": device_b, "C": device_c}
    layer = _build_integration_layer(devices=devices)

    include_filters = [IncludeDeviceByName(name="A")]

    result = layer.get_devices(include_filters=include_filters)

    result_names = sorted([dev._name for dev in result])
    verification.assert_equal(result_names, ["A"])


def test_get_devices_with_exclude_filter_drops_only_matching_device_no_duplicates() -> None:
    """Regression: exclude loop previously had a missing break causing duplicate
    appends, and inverted semantics keeping only the excluded device.
    """
    device_a = _build_device(name="A")
    device_b = _build_device(name="B")
    device_c = _build_device(name="C")
    devices = {"A": device_a, "B": device_b, "C": device_c}
    layer = _build_integration_layer(devices=devices)

    exclude_filters = [ExcludeDeviceByName(name="B")]

    result = layer.get_devices(exclude_filters=exclude_filters)

    result_names = sorted([dev._name for dev in result])
    verification.assert_equal(result_names, ["A", "C"])
    verification.assert_equal(len(result), 2)


def test_get_devices_with_combined_include_and_exclude_filters() -> None:
    device_a = _build_device(name="A")
    device_b = _build_device(name="B")
    device_c = _build_device(name="C")
    devices = {"A": device_a, "B": device_b, "C": device_c}
    layer = _build_integration_layer(devices=devices)

    include_filters = [
        IncludeDeviceByName(name="A"),
        IncludeDeviceByName(name="B"),
    ]
    exclude_filters = [ExcludeDeviceByName(name="B")]

    result = layer.get_devices(include_filters=include_filters, exclude_filters=exclude_filters)

    result_names = sorted([dev._name for dev in result])
    verification.assert_equal(result_names, ["A"])


def test_get_devices_with_two_overlapping_exclude_filters_drops_target_exactly_once() -> None:
    """Regression: when two exclude filters could each independently exclude
    the same device, the buggy loop double-counted the device because the
    inner loop had no ``break``.  Today it should exit once per device.
    """
    device_a = _build_device(name="A", device_type="router")
    device_b = _build_device(name="B", device_type="switch")
    devices = {"A": device_a, "B": device_b}
    layer = _build_integration_layer(devices=devices)

    # Two filters that BOTH exclude device B (by name and by name-again).
    exclude_filters = [
        ExcludeDeviceByName(name="B"),
        ExcludeDeviceByName(name="B"),
    ]

    result = layer.get_devices(exclude_filters=exclude_filters)

    result_names = sorted([dev._name for dev in result])
    verification.assert_equal(result_names, ["A"])
    verification.assert_equal(len(result), 1)


# ---------------------------------------------------------------------------
# get_services() — same shape as get_devices().
# ---------------------------------------------------------------------------


def test_get_services_with_no_filters_returns_all_services() -> None:
    service_a = _build_service(name="A")
    service_b = _build_service(name="B")
    service_c = _build_service(name="C")
    services = {"A": service_a, "B": service_b, "C": service_c}
    layer = _build_integration_layer(services=services)

    result = layer.get_services()

    result_names = sorted([svc._name for svc in result])
    verification.assert_equal(result_names, ["A", "B", "C"])


def test_get_services_with_include_filter_returns_only_matching() -> None:
    service_a = _build_service(name="A")
    service_b = _build_service(name="B")
    service_c = _build_service(name="C")
    services = {"A": service_a, "B": service_b, "C": service_c}
    layer = _build_integration_layer(services=services)

    include_filters = [IncludeServiceByName(name="A")]

    result = layer.get_services(include_filters=include_filters)

    result_names = sorted([svc._name for svc in result])
    verification.assert_equal(result_names, ["A"])


def test_get_services_with_exclude_filter_drops_only_matching_service_no_duplicates() -> None:
    """Regression for the exclude-loop bug, mirrored on the services path."""
    service_a = _build_service(name="A")
    service_b = _build_service(name="B")
    service_c = _build_service(name="C")
    services = {"A": service_a, "B": service_b, "C": service_c}
    layer = _build_integration_layer(services=services)

    exclude_filters = [ExcludeServiceByName(name="B")]

    result = layer.get_services(exclude_filters=exclude_filters)

    result_names = sorted([svc._name for svc in result])
    verification.assert_equal(result_names, ["A", "C"])
    verification.assert_equal(len(result), 2)


def test_get_services_with_combined_include_and_exclude_filters() -> None:
    service_a = _build_service(name="A")
    service_b = _build_service(name="B")
    service_c = _build_service(name="C")
    services = {"A": service_a, "B": service_b, "C": service_c}
    layer = _build_integration_layer(services=services)

    include_filters = [
        IncludeServiceByName(name="A"),
        IncludeServiceByName(name="B"),
    ]
    exclude_filters = [ExcludeServiceByName(name="B")]

    result = layer.get_services(include_filters=include_filters, exclude_filters=exclude_filters)

    result_names = sorted([svc._name for svc in result])
    verification.assert_equal(result_names, ["A"])


def test_get_services_with_two_overlapping_exclude_filters_drops_target_exactly_once() -> None:
    """Regression: duplicate-exclude must not double-drop the same service."""
    service_a = _build_service(name="A")
    service_b = _build_service(name="B")
    services = {"A": service_a, "B": service_b}
    layer = _build_integration_layer(services=services)

    exclude_filters = [
        ExcludeServiceByName(name="B"),
        ExcludeServiceByName(name="B"),
    ]

    result = layer.get_services(exclude_filters=exclude_filters)

    result_names = sorted([svc._name for svc in result])
    verification.assert_equal(result_names, ["A"])
    verification.assert_equal(len(result), 1)
