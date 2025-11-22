"""Tests for the include filter implementations."""

import testbase

from automojo.landscaping.includefilters import (
    IncludeDeviceByDeviceType,
    IncludeDeviceByDeviceTypeAndRole,
    IncludeDeviceByGroup,
    IncludeDeviceByName,
    IncludeDeviceByRole,
    IncludeDeviceConfigByDeviceType,
    IncludeServiceByName,
)
from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.landscapeservice import LandscapeService


def _build_device(device_type: str = "router", role: str = "primary", group: str = "core", name: str = "dev0") -> LandscapeDevice:
    device = object.__new__(LandscapeDevice)
    device._device_type = device_type
    device._role = role
    device._group = group
    device._name = name
    return device


def _build_service(name: str = "svc0") -> LandscapeService:
    service = object.__new__(LandscapeService)
    service._name = name
    return service


def test_include_device_by_device_type_matches_device_type() -> None:
    device = _build_device(device_type="switch")
    matcher = IncludeDeviceByDeviceType("switch")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, True)


def test_include_device_by_device_type_rejects_mismatch_and_non_device() -> None:
    device = _build_device(device_type="router")
    matcher = IncludeDeviceByDeviceType("switch")

    include_result = matcher.should_include(device)
    include_non_device = matcher.should_include(object())

    testbase.assert_equal(include_result, False)
    testbase.assert_equal(include_non_device, False)


def test_include_device_by_device_type_and_role_matches_both() -> None:
    device = _build_device(device_type="router", role="backup")
    matcher = IncludeDeviceByDeviceTypeAndRole("router", "backup")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, True)


def test_include_device_by_device_type_and_role_rejects_partial_matches() -> None:
    type_mismatch = _build_device(device_type="switch", role="backup")
    role_mismatch = _build_device(device_type="router", role="primary")
    matcher = IncludeDeviceByDeviceTypeAndRole("router", "backup")

    include_type_mismatch = matcher.should_include(type_mismatch)
    include_role_mismatch = matcher.should_include(role_mismatch)

    testbase.assert_equal(include_type_mismatch, False)
    testbase.assert_equal(include_role_mismatch, False)


def test_include_device_by_group_matches_group() -> None:
    device = _build_device(group="storage")
    matcher = IncludeDeviceByGroup("storage")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, True)


def test_include_device_by_group_rejects_different_group() -> None:
    device = _build_device(group="compute")
    matcher = IncludeDeviceByGroup("storage")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, False)


def test_include_device_by_name_matches_device_name() -> None:
    device = _build_device(name="alpha")
    matcher = IncludeDeviceByName("alpha")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, True)


def test_include_device_by_name_rejects_different_name() -> None:
    device = _build_device(name="beta")
    matcher = IncludeDeviceByName("alpha")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, False)


def test_include_device_by_role_matches_role() -> None:
    device = _build_device(role="primary")
    matcher = IncludeDeviceByRole("primary")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, True)


def test_include_device_by_role_rejects_other_roles() -> None:
    device = _build_device(role="secondary")
    matcher = IncludeDeviceByRole("primary")

    include_result = matcher.should_include(device)

    testbase.assert_equal(include_result, False)


def test_include_device_config_by_device_type_matches_dict() -> None:
    device_config = {"deviceType": "router"}
    matcher = IncludeDeviceConfigByDeviceType("router")

    include_result = matcher.should_include(device_config)

    testbase.assert_equal(include_result, True)


def test_include_device_config_by_device_type_rejects_non_matching_and_non_dict() -> None:
    mismatched_config = {"deviceType": "switch"}
    matcher = IncludeDeviceConfigByDeviceType("router")

    include_result = matcher.should_include(mismatched_config)
    include_non_dict = matcher.should_include("not a dict")

    testbase.assert_equal(include_result, False)
    testbase.assert_equal(include_non_dict, False)


def test_include_service_by_name_matches_service() -> None:
    service = _build_service(name="api-service")
    matcher = IncludeServiceByName("api-service")

    include_result = matcher.should_include(service)

    testbase.assert_equal(include_result, True)


def test_include_service_by_name_rejects_non_matching_and_non_service() -> None:
    service = _build_service(name="worker-service")
    matcher = IncludeServiceByName("api-service")

    include_result = matcher.should_include(service)
    include_non_service = matcher.should_include(object())

    testbase.assert_equal(include_result, False)
    testbase.assert_equal(include_non_service, False)
