"""
    Tests for the :func:`install_shim` helper that powers every
    ``services/vmware`` backwards-compatibility shim.
"""

import sys
import types
import warnings

from ccai.testbase import verification

from ccai.landscaping.services.vmware import _shim
from ccai.landscaping.services.vmware._shim import install_shim


def test_install_shim_emits_one_warning_and_attaches_symbol() -> None:
    fake_old_path = "ccai.landscaping.services.vmware._test_shim_helper_alpha"
    fake_module = types.ModuleType(fake_old_path)
    sys.modules[fake_old_path] = fake_module
    _shim._WARNED.discard(fake_old_path)

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        install_shim(
            old_path=fake_old_path,
            new_module_name="ccai.restclient.vsphere.vsphereclient",
            public_names=["VSphereClient"],
        )

    dep_warns = [w for w in captured if issubclass(w.category, DeprecationWarning)]
    verification.assert_equal(len(dep_warns), 1)

    from ccai.restclient.vsphere.vsphereclient import VSphereClient

    verification.assert_true(fake_module.VSphereClient is VSphereClient)
    return


def test_install_shim_second_call_same_path_does_not_re_warn() -> None:
    fake_old_path = "ccai.landscaping.services.vmware._test_shim_helper_beta"
    fake_module = types.ModuleType(fake_old_path)
    sys.modules[fake_old_path] = fake_module
    _shim._WARNED.discard(fake_old_path)

    with warnings.catch_warnings(record=True) as first:
        warnings.simplefilter("always")
        install_shim(
            old_path=fake_old_path,
            new_module_name="ccai.restclient.vsphere.vsphereclient",
            public_names=["VSphereClient"],
        )

    first_dep = [w for w in first if issubclass(w.category, DeprecationWarning)]
    verification.assert_equal(len(first_dep), 1)

    with warnings.catch_warnings(record=True) as second:
        warnings.simplefilter("always")
        install_shim(
            old_path=fake_old_path,
            new_module_name="ccai.restclient.vsphere.vsphereclient",
            public_names=["VSphereClient"],
        )

    second_dep = [w for w in second if issubclass(w.category, DeprecationWarning)]
    verification.assert_equal(len(second_dep), 0)
    return


def test_install_shim_resolves_alias_mapping() -> None:
    fake_old_path = "ccai.landscaping.services.vmware._test_shim_helper_gamma"
    fake_module = types.ModuleType(fake_old_path)
    sys.modules[fake_old_path] = fake_module
    _shim._WARNED.discard(fake_old_path)

    install_shim(
        old_path=fake_old_path,
        new_module_name="ccai.restclient.vsphere.vsphereclient",
        public_names=["VSphereAgent"],
        aliases={"VSphereAgent": "VSphereClient"},
    )

    from ccai.restclient.vsphere.vsphereclient import VSphereClient

    verification.assert_true(fake_module.VSphereAgent is VSphereClient)
    return
