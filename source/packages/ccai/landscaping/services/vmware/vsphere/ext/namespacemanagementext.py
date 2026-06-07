"""
    .. module:: namespacemanagementext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports ``NamespaceManagementExt`` from
               ``ccai.restclient.vsphere.apigroups.namespacemanagementgroup``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The legacy ``NamespaceManagementExt`` class was renamed to ``NamespaceManagementGroup`` and moved into the
    ``codecraftai-restclient-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle. Importing this module emits a
    :class:`DeprecationWarning` exactly once per process. New code should use::

        from ccai.restclient.vsphere.apigroups.namespacemanagementgroup import NamespaceManagementGroup
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="ccai.restclient.vsphere.apigroups.namespacemanagementgroup",
    public_names=["NamespaceManagementExt"],
    aliases={"NamespaceManagementExt": "NamespaceManagementGroup"},
)
