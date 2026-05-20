"""
    .. module:: vcenter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports vCenter summary DTOs
               from ``automojo.interop.vsphere.model.summary``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The summary DTOs that originally lived here were extracted to the
    ``automojo-interop-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle and emits a single
    :class:`DeprecationWarning` per process. New code should use::

        from automojo.interop.vsphere.model.summary import (
            DatacenterSummary, FolderSummary,
        )
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.model.summary",
    public_names=["DatacenterSummary", "FolderSummary"],
)
