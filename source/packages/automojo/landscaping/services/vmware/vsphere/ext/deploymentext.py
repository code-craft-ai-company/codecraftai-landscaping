"""
    .. module:: deploymentext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DeploymentExt object.

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

class DeploymentExt(BaseExt):
    """
        Extension providing deployment operations for a vSphere agent.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the Deployment extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
