"""Tests for the exclude filter implementations."""

from automojo.testbase import verification

from automojo.landscaping.excludefilters import (
    ExcludeDeviceBase,
    ExcludeDeviceConfigBase,
    ExcludeServiceBase,
    ExcludeDeviceByDeviceType,
    ExcludeDeviceByDeviceTypeAndRole,
    ExcludeDeviceByGroup,
    ExcludeDeviceByName,
    ExcludeDeviceByRole,
    ExcludeDeviceConfigByDeviceType,
    ExcludeServiceByName,
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


def test_exclude_device_base_is_abstract() -> None:
    raised = False
    try:
        ExcludeDeviceBase()
    except TypeError:
        raised = True

    verification.assert_equal(raised, True)


def test_exclude_device_config_base_is_abstract() -> None:
    raised = False
    try:
        ExcludeDeviceConfigBase()
    except TypeError:
        raised = True

    verification.assert_equal(raised, True)


def test_exclude_service_base_is_abstract() -> None:
    raised = False
    try:
        ExcludeServiceBase()
    except TypeError:
        raised = True

    verification.assert_equal(raised, True)


def test_exclude_device_by_device_type_excludes_match() -> None:
    device = _build_device(device_type="switch")
    matcher = ExcludeDeviceByDeviceType(device_type="switch")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, True)


def test_exclude_device_by_device_type_does_not_exclude_nonmatch() -> None:
    device = _build_device(device_type="router")
    matcher = ExcludeDeviceByDeviceType(device_type="switch")

    exclude_result = matcher.should_exclude(device)
    exclude_non_device = matcher.should_exclude(object())

    verification.assert_equal(exclude_result, False)
    verification.assert_equal(exclude_non_device, False)


def test_exclude_device_by_device_type_and_role_excludes_match() -> None:
    device = _build_device(device_type="router", role="backup")
    matcher = ExcludeDeviceByDeviceTypeAndRole(device_type="router", role="backup")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, True)


def test_exclude_device_by_device_type_and_role_does_not_exclude_nonmatch() -> None:
    type_mismatch = _build_device(device_type="switch", role="backup")
    role_mismatch = _build_device(device_type="router", role="primary")
    matcher = ExcludeDeviceByDeviceTypeAndRole(device_type="router", role="backup")

    exclude_type_mismatch = matcher.should_exclude(type_mismatch)
    exclude_role_mismatch = matcher.should_exclude(role_mismatch)

    verification.assert_equal(exclude_type_mismatch, False)
    verification.assert_equal(exclude_role_mismatch, False)


def test_exclude_device_by_group_excludes_match() -> None:
    device = _build_device(group="storage")
    matcher = ExcludeDeviceByGroup(group="storage")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, True)


def test_exclude_device_by_group_does_not_exclude_nonmatch() -> None:
    device = _build_device(group="compute")
    matcher = ExcludeDeviceByGroup(group="storage")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, False)


def test_exclude_device_by_name_excludes_match() -> None:
    device = _build_device(name="alpha")
    matcher = ExcludeDeviceByName(name="alpha")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, True)


def test_exclude_device_by_name_does_not_exclude_nonmatch() -> None:
    device = _build_device(name="beta")
    matcher = ExcludeDeviceByName(name="alpha")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, False)


def test_exclude_device_by_name_with_empty_name_does_not_exclude_nonempty() -> None:
    device = _build_device(name="alpha")
    matcher = ExcludeDeviceByName(name="")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, False)


def test_exclude_device_by_role_excludes_match() -> None:
    device = _build_device(role="primary")
    matcher = ExcludeDeviceByRole(role="primary")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, True)


def test_exclude_device_by_role_does_not_exclude_nonmatch() -> None:
    device = _build_device(role="secondary")
    matcher = ExcludeDeviceByRole(role="primary")

    exclude_result = matcher.should_exclude(device)

    verification.assert_equal(exclude_result, False)


def test_exclude_device_config_by_device_type_excludes_match() -> None:
    device_config = {"deviceType": "router"}
    matcher = ExcludeDeviceConfigByDeviceType(device_type="router")

    exclude_result = matcher.should_exclude(device_config)

    verification.assert_equal(exclude_result, True)


def test_exclude_device_config_by_device_type_does_not_exclude_nonmatch() -> None:
    mismatched_config = {"deviceType": "switch"}
    matcher = ExcludeDeviceConfigByDeviceType(device_type="router")

    exclude_result = matcher.should_exclude(mismatched_config)
    exclude_non_dict = matcher.should_exclude("not a dict")

    verification.assert_equal(exclude_result, False)
    verification.assert_equal(exclude_non_dict, False)


def test_exclude_service_by_name_excludes_match() -> None:
    service = _build_service(name="api-service")
    matcher = ExcludeServiceByName(name="api-service")

    exclude_result = matcher.should_exclude(service)

    verification.assert_equal(exclude_result, True)


def test_exclude_service_by_name_does_not_exclude_nonmatch() -> None:
    service = _build_service(name="worker-service")
    matcher = ExcludeServiceByName(name="api-service")

    exclude_result = matcher.should_exclude(service)
    exclude_non_service = matcher.should_exclude(object())

    verification.assert_equal(exclude_result, False)
    verification.assert_equal(exclude_non_service, False)


def test_exclude_service_by_name_with_empty_name_does_not_exclude_nonempty() -> None:
    service = _build_service(name="api-service")
    matcher = ExcludeServiceByName(name="")

    exclude_result = matcher.should_exclude(service)

    verification.assert_equal(exclude_result, False)
