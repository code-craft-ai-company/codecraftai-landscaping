"""
    Tests for :class:`LandscapeConfigurationLayer.get_device_configs`.

    Coverage focuses on the bug-prone area called out in the recent five-pass
    audit: the exclude-filter loop in ``get_device_configs`` shared the same
    duplicate-add and inverted-semantic bug as its sibling layer methods
    (pass 4).
"""

from typing import List, Optional
from unittest.mock import MagicMock

from ccai.testbase import verification

from ccai.landscaping.excludefilters import ExcludeDeviceConfigByDeviceType
from ccai.landscaping.includefilters import IncludeDeviceConfigByDeviceType
from ccai.landscaping.layers.landscapeconfigurationlayer import LandscapeConfigurationLayer


def _build_fake_landscape() -> MagicMock:
    """
        Builds a mock landscape whose ``begin_locked_landscape_scope`` returns
        a context manager that enters/exits cleanly.

        :returns: A ``MagicMock`` standing in for a Landscape object.
    """
    fake_lscape = MagicMock()
    fake_scope = MagicMock()
    fake_scope.__enter__ = MagicMock(return_value=fake_scope)
    fake_scope.__exit__ = MagicMock(return_value=False)
    fake_lscape.begin_locked_landscape_scope.return_value = fake_scope
    return fake_lscape


def _build_configuration_layer(device_configs: Optional[List[dict]] = None) -> LandscapeConfigurationLayer:
    """
        Builds a minimally-initialised ``LandscapeConfigurationLayer`` whose
        ``locked_get_device_configs`` returns the supplied list.  All other
        methods on the layer remain inert.

        :param device_configs: Pre-populated list of device config dicts that
                               ``locked_get_device_configs`` should return.

        :returns: A test-ready :class:`LandscapeConfigurationLayer` instance.
    """
    layer = object.__new__(LandscapeConfigurationLayer)

    layer._credential_manager = None
    layer._landscape_files = None
    layer._landscape_info = None
    layer._topology_files = None
    layer._topology_info = None

    fake_lscape = _build_fake_landscape()
    layer._lscape_ref = lambda: fake_lscape

    canned_configs = device_configs if device_configs is not None else []

    def _fake_locked_get_device_configs() -> List[dict]:
        # Return a fresh copy each call so the production code's ``.pop()``
        # cannot leak into the test fixture.
        copy_of_configs = [item for item in canned_configs]
        return copy_of_configs

    layer.locked_get_device_configs = _fake_locked_get_device_configs

    return layer


def _build_device_config(device_type: str = "router", name: str = "dev0") -> dict:
    """
        Constructs a dict mimicking a device configuration entry.

        :param device_type: The device type label.
        :param name: The device name.

        :returns: A dict with ``deviceType`` and ``name`` keys populated.
    """
    config = {"deviceType": device_type, "name": name}
    return config


# ---------------------------------------------------------------------------
# get_device_configs() — public contract + regression for exclude bug.
# ---------------------------------------------------------------------------


def test_get_device_configs_with_no_filters_returns_all_configs() -> None:
    config_a = _build_device_config(device_type="router", name="A")
    config_b = _build_device_config(device_type="switch", name="B")
    config_c = _build_device_config(device_type="router", name="C")
    layer = _build_configuration_layer(device_configs=[config_a, config_b, config_c])

    result = layer.get_device_configs()

    result_names = sorted([cfg["name"] for cfg in result])
    verification.assert_equal(result_names, ["A", "B", "C"])


def test_get_device_configs_with_include_filter_returns_only_matching() -> None:
    config_a = _build_device_config(device_type="router", name="A")
    config_b = _build_device_config(device_type="switch", name="B")
    config_c = _build_device_config(device_type="router", name="C")
    layer = _build_configuration_layer(device_configs=[config_a, config_b, config_c])

    include_filters = [IncludeDeviceConfigByDeviceType(device_type="switch")]

    result = layer.get_device_configs(include_filters=include_filters)

    result_names = sorted([cfg["name"] for cfg in result])
    verification.assert_equal(result_names, ["B"])


def test_get_device_configs_with_exclude_filter_drops_only_matching_no_duplicates() -> None:
    """Regression: exclude loop previously had a missing break causing duplicate
    appends, plus inverted semantics keeping only the excluded config.
    """
    config_a = _build_device_config(device_type="router", name="A")
    config_b = _build_device_config(device_type="switch", name="B")
    config_c = _build_device_config(device_type="router", name="C")
    layer = _build_configuration_layer(device_configs=[config_a, config_b, config_c])

    exclude_filters = [ExcludeDeviceConfigByDeviceType(device_type="switch")]

    result = layer.get_device_configs(exclude_filters=exclude_filters)

    result_names = sorted([cfg["name"] for cfg in result])
    verification.assert_equal(result_names, ["A", "C"])
    verification.assert_equal(len(result), 2)


def test_get_device_configs_with_combined_include_and_exclude_filters() -> None:
    config_a = _build_device_config(device_type="router", name="A")
    config_b = _build_device_config(device_type="switch", name="B")
    config_c = _build_device_config(device_type="router", name="C")
    layer = _build_configuration_layer(device_configs=[config_a, config_b, config_c])

    include_filters = [
        IncludeDeviceConfigByDeviceType(device_type="router"),
        IncludeDeviceConfigByDeviceType(device_type="switch"),
    ]
    exclude_filters = [ExcludeDeviceConfigByDeviceType(device_type="switch")]

    result = layer.get_device_configs(include_filters=include_filters, exclude_filters=exclude_filters)

    result_names = sorted([cfg["name"] for cfg in result])
    verification.assert_equal(result_names, ["A", "C"])


def test_get_device_configs_with_two_overlapping_exclude_filters_drops_target_exactly_once() -> None:
    """Regression: duplicate-exclude must not double-drop the same config.

    The buggy version had an inner loop with no break statement, which meant
    a config could be appended to the result list more than once when more
    than one filter said to exclude it.
    """
    config_a = _build_device_config(device_type="router", name="A")
    config_b = _build_device_config(device_type="switch", name="B")
    layer = _build_configuration_layer(device_configs=[config_a, config_b])

    exclude_filters = [
        ExcludeDeviceConfigByDeviceType(device_type="switch"),
        ExcludeDeviceConfigByDeviceType(device_type="switch"),
    ]

    result = layer.get_device_configs(exclude_filters=exclude_filters)

    result_names = sorted([cfg["name"] for cfg in result])
    verification.assert_equal(result_names, ["A"])
    verification.assert_equal(len(result), 1)
