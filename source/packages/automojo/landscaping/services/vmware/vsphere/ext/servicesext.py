"""
    .. module:: servicesext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``ServicesExt`` from
               ``automojo.interop.vsphere.apigroups.servicesgroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``ServicesExt`` class was renamed to ``ServicesGroup`` and moved into the
    ``automojo-interop-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.interop.vsphere.apigroups.servicesgroup import ServicesGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.apigroups.servicesgroup",
    public_names=["ServicesExt"],
    aliases={"ServicesExt": "ServicesGroup"},
)
