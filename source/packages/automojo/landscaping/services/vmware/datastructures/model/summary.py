"""
    .. module:: summary
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports summary DTOs from
               ``automojo.restclient.vsphere.model.summary``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The summary DTOs that originally lived here were extracted to the
    ``automojo-restclient-vsphere`` package during M5. ``DatacenterSummary`` and
    ``FolderSummary`` re-export from the new module. ``VmSummary`` was retired
    in favour of the richer :class:`VirtualMachineSummary` in the new package
    and is no longer re-exported; consumers should migrate to the new type.

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from automojo.restclient.vsphere.model.summary import (
            DatacenterSummary, FolderSummary,
        )
        from automojo.restclient.vsphere.model.vm import VirtualMachineSummary
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.model.summary",
    public_names=["DatacenterSummary", "FolderSummary"],
)
