"""
    .. module:: vmplacement
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports
               :class:`VmPlacementSpec` from
               ``ccai.restclient.vsphere.specs.vmplacement``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from ccai.restclient.vsphere.specs.vmplacement import VmPlacementSpec
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="ccai.restclient.vsphere.specs.vmplacement",
    public_names=["VmPlacementSpec"],
)
