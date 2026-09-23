"""
    Tests asserting that each shim emits :class:`DeprecationWarning` exactly
    once per process per old-import-path, even when imported from many call
    sites.
"""

import importlib
import warnings

from ccai.testbase import verification

from ccai.landscaping.services.vmware import _shim


def test_vsphereagent_shim_warns_only_once_per_process() -> None:
    target_path = "ccai.landscaping.services.vmware.vsphere.vsphereagent"

    _shim._WARNED.discard(target_path)

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")

        first_module = importlib.import_module(target_path)
        importlib.reload(first_module)
        second_module = importlib.import_module(target_path)
        importlib.reload(second_module)

    matching = [
        w for w in captured
        if issubclass(w.category, DeprecationWarning) and target_path in str(w.message)
    ]
    verification.assert_equal(len(matching), 1)
    return


def test_vmext_shim_warns_only_once_per_process() -> None:
    target_path = "ccai.landscaping.services.vmware.vsphere.ext.vmext"

    _shim._WARNED.discard(target_path)

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")

        first_module = importlib.import_module(target_path)
        importlib.reload(first_module)
        second_module = importlib.import_module(target_path)
        importlib.reload(second_module)

    matching = [
        w for w in captured
        if issubclass(w.category, DeprecationWarning) and target_path in str(w.message)
    ]
    verification.assert_equal(len(matching), 1)
    return


def test_metasphere_vcenter_shim_warns_only_once_per_process() -> None:
    target_path = "ccai.landscaping.services.vmware.metasphere.vcenter"

    _shim._WARNED.discard(target_path)

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")

        first_module = importlib.import_module(target_path)
        importlib.reload(first_module)
        second_module = importlib.import_module(target_path)
        importlib.reload(second_module)

    matching = [
        w for w in captured
        if issubclass(w.category, DeprecationWarning) and target_path in str(w.message)
    ]
    verification.assert_equal(len(matching), 1)
    return
