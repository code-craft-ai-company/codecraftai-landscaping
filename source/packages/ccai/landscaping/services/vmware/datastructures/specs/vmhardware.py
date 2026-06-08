"""
    .. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports :class:`VmHardwareSpec`
               from ``ccai.restclient.vsphere.specs.vmhardware``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The fine-grained legacy VM-hardware ``*CreateSpec`` / ``*UpdateSpec``
    dataclasses that lived here were consolidated into the
    :class:`VmHardwareSpec` SchemaObject in the new
    ``codecraftai-restclient-vsphere`` package during M5. Only that consolidated
    class is re-exported. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from ccai.restclient.vsphere.specs.vmhardware import VmHardwareSpec
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="ccai.restclient.vsphere.specs.vmhardware",
    public_names=["VmHardwareSpec"],
)
