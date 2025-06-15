"""
    .. module:: namespacesext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the NamespacesExt object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from  http import HTTPStatus

from automojo.landscaping.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent

class NamespacesExt(BaseExt):
    """
        Extension that manages the vSphere namespaces API.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the namespaces extension.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
