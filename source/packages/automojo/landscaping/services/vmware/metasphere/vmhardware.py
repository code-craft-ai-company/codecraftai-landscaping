"""
    .. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports the VM hardware
               version enum from
               ``automojo.restclient.vsphere.enums.hardwareversion``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``VmHardwareVersion`` enum was renamed :class:`HardwareVersion`
    and moved into the ``automojo-restclient-vsphere`` package during M5. The
    other fine-grained backing-type / adapter-type enums that lived here are no
    longer enumerated and have been replaced by plain string fields on the new
    :class:`VmHardwareSpec` SchemaObject; callers that depended on them should
    migrate to plain strings.

    Importing this module emits a :class:`DeprecationWarning` exactly once per
    process. New code should use::

        from automojo.restclient.vsphere.enums.hardwareversion import HardwareVersion
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.enums.hardwareversion",
    public_names=["VmHardwareVersion"],
    aliases={"VmHardwareVersion": "HardwareVersion"},
)
