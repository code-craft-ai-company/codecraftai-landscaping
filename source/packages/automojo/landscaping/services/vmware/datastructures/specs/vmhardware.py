"""
    .. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports :class:`VmHardwareSpec`
               from ``automojo.restclient.vsphere.specs.vmhardware``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The fine-grained legacy VM-hardware ``*CreateSpec`` / ``*UpdateSpec``
    dataclasses that lived here were consolidated into the
    :class:`VmHardwareSpec` SchemaObject in the new
    ``automojo-restclient-vsphere`` package during M5. Only that consolidated
    class is re-exported. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.restclient.vsphere.specs.vmhardware import VmHardwareSpec
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.specs.vmhardware",
    public_names=["VmHardwareSpec"],
)
