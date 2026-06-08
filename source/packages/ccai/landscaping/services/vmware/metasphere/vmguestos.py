"""
    .. module:: vmguestos
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports the guest OS enum
               from ``ccai.restclient.vsphere.enums.guestos``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``VmGuestOS`` enum was renamed :class:`GuestOs` and moved into
    the ``codecraftai-restclient-vsphere`` package during M5. Importing this module
    emits a :class:`DeprecationWarning` exactly once per process. New code
    should use::

        from ccai.restclient.vsphere.enums.guestos import GuestOs
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="ccai.restclient.vsphere.enums.guestos",
    public_names=["VmGuestOS"],
    aliases={"VmGuestOS": "GuestOs"},
)
