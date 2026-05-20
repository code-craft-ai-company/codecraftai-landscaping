"""
    .. module:: vcenter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports vCenter enumerations
               from ``automojo.interop.vsphere.enums.powerstate``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``VmPowerState`` enum was renamed :class:`PowerState` and moved
    into the ``automojo-interop-vsphere`` package during M5. The legacy
    ``FolderType`` enum did not survive the migration — folder type is now
    carried as a plain string field on :class:`FolderSummary`. Callers that
    depended on ``FolderType`` should migrate to plain strings.

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from automojo.interop.vsphere.enums.powerstate import PowerState
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.enums.powerstate",
    public_names=["VmPowerState"],
    aliases={"VmPowerState": "PowerState"},
)
