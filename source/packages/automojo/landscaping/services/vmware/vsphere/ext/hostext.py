"""
    .. module:: hostext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the HostExt object.

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

class HostExt(BaseExt):
    """
        Extension that manages host interactions for a vSphere agent.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the Host extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
    
    def connect(self, host: str):
        """
            Connects a host to vCenter.

            :param host: Identifier of the host to connect.
        """
        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/host/{host}")
        resp = agent.session_post(req_url, action="connect")

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def delete(self, host: str):
        """
            Deletes a host from vCenter inventory.

            :param host: Identifier of the host to delete.
        """
        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/host/{host}")
        resp = agent.session_delete(req_url)

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def disconnect(self, host: str):
        """
            Disconnects a host from vCenter.

            :param host: Identifier of the host to disconnect.
        """
        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/host/{host}")
        resp = agent.session_post(req_url, action="disconnect")

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def list(self):
        """
            Lists hosts known to vCenter.

            :returns: List of host records.
        """
        host_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/host")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            host_list = resp.json()
        else:
            resp.raise_for_status()

        return host_list