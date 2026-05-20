"""
    .. module:: vmplacement
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports
               :class:`VmPlacementSpec` from
               ``automojo.restclient.vsphere.specs.vmplacement``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from automojo.restclient.vsphere.specs.vmplacement import VmPlacementSpec
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.specs.vmplacement",
    public_names=["VmPlacementSpec"],
)
