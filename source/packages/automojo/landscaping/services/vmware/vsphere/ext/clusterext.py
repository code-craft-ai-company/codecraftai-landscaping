"""
    .. module:: clusterext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``ClusterExt`` from
               ``automojo.interop.vsphere.apigroups.clustergroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``ClusterExt`` class was renamed to ``ClusterGroup`` and moved into the
    ``automojo-interop-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.interop.vsphere.apigroups.clustergroup import ClusterGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.apigroups.clustergroup",
    public_names=["ClusterExt"],
    aliases={"ClusterExt": "ClusterGroup"},
)
