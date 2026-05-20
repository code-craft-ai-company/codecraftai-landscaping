"""
    .. module:: vm
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — points consumers at the new
               vSphere VM model classes.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The fine-grained legacy VM hardware DTOs that used to live here were
    consolidated into :class:`VirtualMachineInfo` and
    :class:`VirtualMachineSummary` in
    ``automojo.restclient.vsphere.model.vm`` during M5. Those two classes are
    re-exported here for one release cycle. Legacy detail-level dataclasses are
    no longer available — callers that depended on them should migrate to the
    consolidated info objects.

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from automojo.restclient.vsphere.model.vm import (
            VirtualMachineSummary, VirtualMachineInfo,
        )
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.model.vm",
    public_names=["VirtualMachineSummary", "VirtualMachineInfo"],
)
