"""
    .. module:: vmguestos
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports the guest OS enum
               from ``automojo.interop.vsphere.enums.guestos``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``VmGuestOS`` enum was renamed :class:`GuestOs` and moved into
    the ``automojo-interop-vsphere`` package during M5. Importing this module
    emits a :class:`DeprecationWarning` exactly once per process. New code
    should use::

        from automojo.interop.vsphere.enums.guestos import GuestOs
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.enums.guestos",
    public_names=["VmGuestOS"],
    aliases={"VmGuestOS": "GuestOs"},
)
