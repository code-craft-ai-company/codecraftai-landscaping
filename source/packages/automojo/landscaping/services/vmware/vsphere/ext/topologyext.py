"""
    .. module:: topologyext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``TopologyExt`` from
               ``automojo.interop.vsphere.apigroups.topologygroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``TopologyExt`` class was renamed to ``TopologyGroup`` and moved into the
    ``automojo-interop-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.interop.vsphere.apigroups.topologygroup import TopologyGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.apigroups.topologygroup",
    public_names=["TopologyExt"],
    aliases={"TopologyExt": "TopologyGroup"},
)
