"""
    .. module:: networkext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the NetworkExt object.

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

class NetworkExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the network extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
    
    def list(self):
        """
            Retrieves a list of networks from vCenter.

            :returns: List of network records.
        """
        network_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/network")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            network_list = resp.json()
        else:
            resp.raise_for_status()

        return network_list
