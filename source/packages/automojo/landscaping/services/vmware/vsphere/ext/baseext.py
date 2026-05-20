"""
    .. module:: baseext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``BaseExt`` from
               ``automojo.restclient.vsphere.apigroups.basegroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``BaseExt`` class was renamed to ``BaseGroup`` and moved into the
    ``automojo-restclient-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.restclient.vsphere.apigroups.basegroup import BaseGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.apigroups.basegroup",
    public_names=["BaseExt"],
    aliases={"BaseExt": "BaseGroup"},
)
