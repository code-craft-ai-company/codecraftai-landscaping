"""
    .. module:: vcenter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatibility shim — re-exports vCenter summary DTOs
               from ``ccai.restclient.vsphere.model.summary``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The summary DTOs that originally lived here were extracted to the
    ``codecraftai-restclient-vsphere`` package during M5. This shim preserves the
    legacy import path for one release cycle and emits a single
    :class:`DeprecationWarning` per process. New code should use::

        from ccai.restclient.vsphere.model.summary import (
            DatacenterSummary, FolderSummary,
        )
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.landscaping.services.vmware._shim import install_shim


install_shim(
    old_path=__name__,
    new_module_name="ccai.restclient.vsphere.model.summary",
    public_names=["DatacenterSummary", "FolderSummary"],
)
