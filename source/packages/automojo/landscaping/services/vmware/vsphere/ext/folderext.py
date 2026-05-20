"""
    .. module:: folderext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``FolderExt`` from
               ``automojo.interop.vsphere.apigroups.foldergroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``FolderExt`` class was renamed to ``FolderGroup`` and moved into the
    ``automojo-interop-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.interop.vsphere.apigroups.foldergroup import FolderGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.apigroups.foldergroup",
    public_names=["FolderExt"],
    aliases={"FolderExt": "FolderGroup"},
)
