"""
    .. module:: storageext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``StorageExt`` from
               ``automojo.restclient.vsphere.apigroups.storagegroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``StorageExt`` class was renamed to ``StorageGroup`` and moved into the
    ``automojo-restclient-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.restclient.vsphere.apigroups.storagegroup import StorageGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.apigroups.storagegroup",
    public_names=["StorageExt"],
    aliases={"StorageExt": "StorageGroup"},
)
