"""
    .. module:: systemconfigext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``SystemConfigExt`` from
               ``automojo.restclient.vsphere.apigroups.systemconfiggroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``SystemConfigExt`` class was renamed to ``SystemConfigGroup`` and moved into the
    ``automojo-restclient-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.restclient.vsphere.apigroups.systemconfiggroup import SystemConfigGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.apigroups.systemconfiggroup",
    public_names=["SystemConfigExt"],
    aliases={"SystemConfigExt": "SystemConfigGroup"},
)
