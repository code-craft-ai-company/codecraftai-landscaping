"""
    .. module:: identityext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the IdentityExt object.

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

class IdentityExt(BaseExt):
    """
        Extension that wraps vSphere identity management APIs.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the identity extension.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
