"""
    .. module:: vsphereagent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``VSphereAgent`` from
               its new home in ``automojo.restclient.vsphere.vsphereclient``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``VSphereAgent`` class was renamed to ``VSphereClient`` and moved
    into the ``automojo-restclient-vsphere`` package during M5. This shim preserves
    the legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from automojo.restclient.vsphere.vsphereclient import VSphereClient
        from automojo.restclient.vsphere.vspherefilterstate import VSphereFilterState
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.vsphereclient",
    public_names=["VSphereAgent"],
    aliases={"VSphereAgent": "VSphereClient"},
)

# Also re-export VSphereFilterState (lived in this module legacy-side). The
# warning has already been emitted by the first install_shim call above; a
# second call with the same old_path is silent and just attaches symbols.
install_shim(
    old_path=__name__,
    new_module_name="automojo.restclient.vsphere.vspherefilterstate",
    public_names=["VSphereFilterState"],
)
