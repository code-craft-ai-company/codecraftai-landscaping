"""
    Tests asserting that each legacy shim path under
    ``automojo.landscaping.services.vmware`` re-exports the same class object
    that the new ``automojo-interop-vsphere`` module exposes.
"""

import warnings

from automojo.testbase import verification


def test_vsphereagent_shim_aliases_vsphereclient() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent
        from automojo.interop.vsphere.vsphereclient import VSphereClient

    verification.assert_true(VSphereAgent is VSphereClient)
    return


def test_vsphereagent_shim_also_reexports_filterstate() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereFilterState as LegacyFilterState
        from automojo.interop.vsphere.vspherefilterstate import VSphereFilterState as NewFilterState

    verification.assert_true(LegacyFilterState is NewFilterState)
    return


def test_vmext_shim_aliases_vmgroup() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.vsphere.ext.vmext import VmExt
        from automojo.interop.vsphere.apigroups.vmgroup import VmGroup

    verification.assert_true(VmExt is VmGroup)
    return


def test_clusterext_shim_aliases_clustergroup() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.vsphere.ext.clusterext import ClusterExt
        from automojo.interop.vsphere.apigroups.clustergroup import ClusterGroup

    verification.assert_true(ClusterExt is ClusterGroup)
    return


def test_datacenterext_shim_aliases_datacentergroup() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.vsphere.ext.datacenterext import DataCenterExt
        from automojo.interop.vsphere.apigroups.datacentergroup import DatacenterGroup

    verification.assert_true(DataCenterExt is DatacenterGroup)
    return


def test_vcenter_datastructures_shim_reexports_summaries() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.datastructures.vcenter import (
            DatacenterSummary,
            FolderSummary,
        )
        from automojo.interop.vsphere.model.summary import (
            DatacenterSummary as NewDatacenterSummary,
            FolderSummary as NewFolderSummary,
        )

    verification.assert_true(DatacenterSummary is NewDatacenterSummary)
    verification.assert_true(FolderSummary is NewFolderSummary)
    return


def test_vmplacement_spec_shim_reexports() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.datastructures.specs.vmplacement import VmPlacementSpec
        from automojo.interop.vsphere.specs.vmplacement import VmPlacementSpec as NewVmPlacementSpec

    verification.assert_true(VmPlacementSpec is NewVmPlacementSpec)
    return


def test_metasphere_vcenter_shim_aliases_powerstate() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.metasphere.vcenter import VmPowerState
        from automojo.interop.vsphere.enums.powerstate import PowerState

    verification.assert_true(VmPowerState is PowerState)
    return


def test_metasphere_vmguestos_shim_aliases_guestos() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from automojo.landscaping.services.vmware.metasphere.vmguestos import VmGuestOS
        from automojo.interop.vsphere.enums.guestos import GuestOs

    verification.assert_true(VmGuestOS is GuestOs)
    return
