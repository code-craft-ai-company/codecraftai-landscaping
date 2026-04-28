"""
    Tests for :class:`LandscapeOperationalLayer` filter and checkin paths.

    Coverage focuses on the bug-prone areas called out in the recent five-pass
    audit:

      * ``get_clusters`` exclude-filter loop — regression for the duplicate-add
        and inverted-semantic bugs (pass 4).
      * ``checkin_cluster`` / ``checkin_device`` / ``checkin_control_point``
        error-message construction — regression for the implicit-string-concat
        bugs (pass 1) where two adjacent literal strings without a comma were
        glued onto one line instead of being two distinct list entries.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from automojo.testbase import verification

from automojo.errors.exceptions import CheckinError

from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.landscapedevicecluster import LandscapeDeviceCluster
from automojo.landscaping.layers.landscapeoperationallayer import LandscapeOperationalLayer


class _IncludeClusterByName:
    """
        Minimal include-by-name filter for clusters used inside these tests.

        The shipped include filter set targets devices/services/configs only, so
        a cluster-flavoured stand-in keeps these tests independent of those
        higher-level types.
    """

    def __init__(self, name: str) -> None:
        """
            Records the cluster name to match on.

            :param name: The cluster name to include.
        """
        self._name = name
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Indicates whether ``check_object`` matches the include criteria.

            :param check_object: A :class:`LandscapeDeviceCluster` candidate.

            :returns: ``True`` when the cluster's name matches.
        """
        include = False
        if isinstance(check_object, LandscapeDeviceCluster):
            if check_object.name == self._name:
                include = True
        return include


class _ExcludeClusterByName:
    """
        Minimal exclude-by-name filter for clusters used inside these tests.
    """

    def __init__(self, name: str) -> None:
        """
            Records the cluster name to match on.

            :param name: The cluster name to exclude.
        """
        self._name = name
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Indicates whether ``check_object`` matches the exclude criteria.

            :param check_object: A :class:`LandscapeDeviceCluster` candidate.

            :returns: ``True`` when the cluster's name matches.
        """
        exclude = False
        if isinstance(check_object, LandscapeDeviceCluster):
            if check_object.name == self._name:
                exclude = True
        return exclude


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


def _build_operational_layer(
    operational_clusters: Optional[Dict[str, LandscapeDeviceCluster]] = None,
    clusters_pool: Optional[Dict[str, LandscapeDeviceCluster]] = None,
    clusters_outstanding: Optional[Dict[str, LandscapeDeviceCluster]] = None,
    device_pool: Optional[Dict[str, LandscapeDevice]] = None,
    device_outstanding: Optional[Dict[str, LandscapeDevice]] = None,
    controlpoint_pool: Optional[Dict[str, Any]] = None,
    controlpoint_outstanding: Optional[Dict[str, Any]] = None,
) -> LandscapeOperationalLayer:
    """
        Builds a minimally-initialised ``LandscapeOperationalLayer`` that
        bypasses the heavyweight constructor.  Only the attributes exercised by
        the methods under test are seeded.

        :param operational_clusters: Pre-populated operational clusters table.
        :param clusters_pool: Pre-populated available cluster pool.
        :param clusters_outstanding: Pre-populated outstanding cluster set.
        :param device_pool: Pre-populated available device pool.
        :param device_outstanding: Pre-populated outstanding device set.
        :param controlpoint_pool: Pre-populated control point pool.
        :param controlpoint_outstanding: Pre-populated outstanding control points.

        :returns: A test-ready :class:`LandscapeOperationalLayer` instance.
    """
    layer = object.__new__(LandscapeOperationalLayer)

    layer._operational_clusters = operational_clusters if operational_clusters is not None else {}
    layer._operational_clusters_pool = clusters_pool if clusters_pool is not None else {}
    layer._operational_clusters_outstanding = clusters_outstanding if clusters_outstanding is not None else {}
    layer._operational_device_pool = device_pool if device_pool is not None else {}
    layer._operational_device_outstanding = device_outstanding if device_outstanding is not None else {}
    layer._operational_controlpoint_pool = controlpoint_pool if controlpoint_pool is not None else {}
    layer._operational_controlpoint_outstanding = controlpoint_outstanding if controlpoint_outstanding is not None else {}

    fake_lscape = _build_fake_landscape()
    layer._lscape_ref = lambda: fake_lscape

    return layer


def _build_cluster(name: str = "cluster0") -> LandscapeDeviceCluster:
    """
        Constructs a minimally-initialised :class:`LandscapeDeviceCluster`.

        :param name: The cluster name.

        :returns: A bare :class:`LandscapeDeviceCluster`.
    """
    cluster = object.__new__(LandscapeDeviceCluster)
    cluster._name = name
    cluster._nodes = {}
    cluster._spares = {}
    cluster._group = None
    return cluster


# ---------------------------------------------------------------------------
# get_clusters() — public contract + regression for exclude bug.
# ---------------------------------------------------------------------------


def test_get_clusters_with_no_filters_returns_all_clusters() -> None:
    cluster_a = _build_cluster(name="A")
    cluster_b = _build_cluster(name="B")
    cluster_c = _build_cluster(name="C")
    clusters = {"A": cluster_a, "B": cluster_b, "C": cluster_c}
    layer = _build_operational_layer(operational_clusters=clusters)

    result = layer.get_clusters()

    result_names = sorted([clu.name for clu in result])
    verification.assert_equal(result_names, ["A", "B", "C"])


def test_get_clusters_with_include_filter_returns_only_matching() -> None:
    cluster_a = _build_cluster(name="A")
    cluster_b = _build_cluster(name="B")
    cluster_c = _build_cluster(name="C")
    clusters = {"A": cluster_a, "B": cluster_b, "C": cluster_c}
    layer = _build_operational_layer(operational_clusters=clusters)

    include_filters = [_IncludeClusterByName(name="A")]

    result = layer.get_clusters(include_filters=include_filters)

    result_names = sorted([clu.name for clu in result])
    verification.assert_equal(result_names, ["A"])


def test_get_clusters_with_exclude_filter_drops_only_matching_cluster_no_duplicates() -> None:
    """Regression: exclude loop previously had a missing break causing duplicate
    appends, plus inverted semantics keeping only the excluded cluster.
    """
    cluster_a = _build_cluster(name="A")
    cluster_b = _build_cluster(name="B")
    cluster_c = _build_cluster(name="C")
    clusters = {"A": cluster_a, "B": cluster_b, "C": cluster_c}
    layer = _build_operational_layer(operational_clusters=clusters)

    exclude_filters = [_ExcludeClusterByName(name="B")]

    result = layer.get_clusters(exclude_filters=exclude_filters)

    result_names = sorted([clu.name for clu in result])
    verification.assert_equal(result_names, ["A", "C"])
    verification.assert_equal(len(result), 2)


def test_get_clusters_with_combined_include_and_exclude_filters() -> None:
    cluster_a = _build_cluster(name="A")
    cluster_b = _build_cluster(name="B")
    cluster_c = _build_cluster(name="C")
    clusters = {"A": cluster_a, "B": cluster_b, "C": cluster_c}
    layer = _build_operational_layer(operational_clusters=clusters)

    include_filters = [
        _IncludeClusterByName(name="A"),
        _IncludeClusterByName(name="B"),
    ]
    exclude_filters = [_ExcludeClusterByName(name="B")]

    result = layer.get_clusters(include_filters=include_filters, exclude_filters=exclude_filters)

    result_names = sorted([clu.name for clu in result])
    verification.assert_equal(result_names, ["A"])


def test_get_clusters_with_two_overlapping_exclude_filters_drops_target_exactly_once() -> None:
    """Regression: duplicate-exclude must not double-drop the same cluster.

    The buggy version had an inner loop with no break statement, which meant
    a cluster could be appended to the result list more than once when more
    than one filter said to exclude it.
    """
    cluster_a = _build_cluster(name="A")
    cluster_b = _build_cluster(name="B")
    clusters = {"A": cluster_a, "B": cluster_b}
    layer = _build_operational_layer(operational_clusters=clusters)

    exclude_filters = [
        _ExcludeClusterByName(name="B"),
        _ExcludeClusterByName(name="B"),
    ]

    result = layer.get_clusters(exclude_filters=exclude_filters)

    result_names = sorted([clu.name for clu in result])
    verification.assert_equal(result_names, ["A"])
    verification.assert_equal(len(result), 1)


# ---------------------------------------------------------------------------
# checkin_*  error-message regression — the implicit-string-concat bug
# (pass 1) glued the "AVAILABLE POOL:" header onto the previous summary line
# instead of placing it on its own line.
# ---------------------------------------------------------------------------


def test_checkin_cluster_unknown_id_raises_checkinerror_with_separated_lines() -> None:
    layer = _build_operational_layer()
    unknown_cluster = _build_cluster(name="ghost")

    raised_error = None
    try:
        layer.checkin_cluster(cluster=unknown_cluster)
    except CheckinError as err:
        raised_error = err

    verification.assert_equal(raised_error is not None, True)

    err_text = str(raised_error)
    has_summary_line = "not previously checked out." in err_text
    has_pool_header = "AVAILABLE POOL:" in err_text
    has_outstanding_header = "OUTSTANDING POOL:" in err_text

    verification.assert_equal(has_summary_line, True)
    verification.assert_equal(has_pool_header, True)
    verification.assert_equal(has_outstanding_header, True)

    # Regression: the summary line and the AVAILABLE POOL header must be on
    # SEPARATE lines.  The implicit-string-concat bug glued them together.
    glued = "not previously checked out.AVAILABLE POOL:"
    is_glued = glued in err_text
    verification.assert_equal(is_glued, False)


def test_checkin_device_unknown_id_raises_checkinerror_with_separated_lines() -> None:
    layer = _build_operational_layer()

    unknown_device = MagicMock()
    unknown_device.identity = "phantom"

    raised_error = None
    try:
        layer.checkin_device(device=unknown_device)
    except CheckinError as err:
        raised_error = err

    verification.assert_equal(raised_error is not None, True)

    err_text = str(raised_error)
    has_summary_line = "not previously checked out." in err_text
    has_pool_header = "AVAILABLE POOL:" in err_text
    has_outstanding_header = "OUTSTANDING POOL:" in err_text

    verification.assert_equal(has_summary_line, True)
    verification.assert_equal(has_pool_header, True)
    verification.assert_equal(has_outstanding_header, True)

    glued = "not previously checked out.AVAILABLE POOL:"
    is_glued = glued in err_text
    verification.assert_equal(is_glued, False)


def test_checkin_control_point_unknown_key_raises_checkinerror_with_separated_lines() -> None:
    layer = _build_operational_layer()

    raised_error = None
    try:
        layer.checkin_control_point(extension=MagicMock(), control_key="phantom-key")
    except CheckinError as err:
        raised_error = err

    verification.assert_equal(raised_error is not None, True)

    err_text = str(raised_error)
    has_summary_line = "not previously checked out." in err_text
    has_pool_header = "AVAILABLE POOL:" in err_text
    has_outstanding_header = "OUTSTANDING POOL:" in err_text

    verification.assert_equal(has_summary_line, True)
    verification.assert_equal(has_pool_header, True)
    verification.assert_equal(has_outstanding_header, True)

    glued = "not previously checked out.AVAILABLE POOL:"
    is_glued = glued in err_text
    verification.assert_equal(is_glued, False)
