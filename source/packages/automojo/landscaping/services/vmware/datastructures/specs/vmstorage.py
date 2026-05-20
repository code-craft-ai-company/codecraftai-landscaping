"""
    .. module:: vmstorage
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports the storage spec
               types from ``automojo.restclient.vsphere.specs.vmstorage``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``VmStoragePolicySpec`` dataclass was superseded by the
    :class:`VmStorageSpec` / :class:`VmDiskSpec` SchemaObjects in the new
    ``automojo-restclient-vsphere`` package during M5. Both new classes are
    re-exported here; the legacy ``VmStoragePolicySpec`` symbol is mapped onto
    :class:`VmStorageSpec` so existing imports resolve.

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from automojo.restclient.vsphere.specs.vmstorage import (
            VmStorageSpec, VmDiskSpec,
        )
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.specs.vmstorage",
    public_names=["VmStorageSpec", "VmDiskSpec", "VmStoragePolicySpec"],
    aliases={"VmStoragePolicySpec": "VmStorageSpec"},
)
