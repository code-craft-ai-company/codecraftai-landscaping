"""
    .. module:: datacenterext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DataCenterExt object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, TYPE_CHECKING

from  http import HTTPStatus

from automojo.landscaping.services.vmware.datastructures.vcenter import (
    DatacenterSummary
)

from automojo.landscaping.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent

class DataCenterExt(BaseExt):
    """
        Extension that manages datacenter objects within vCenter.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Creates a datacenter extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return

    def delete(self, id: str):
        """
            Deletes a datacenter from vCenter inventory.

            :param id: Identifier of the datacenter to delete.
        """

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/datacenter/{id}")
        resp = agent.session_delete(req_url)

        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()
        
        return

    def get(self, id: str) -> DatacenterSummary:
        """
            Retrieves a datacenter summary by identifier.

            :param id: Identifier of the datacenter to retrieve.

            :returns: Datacenter summary instance.
            :rtype: DatacenterSummary
        """

        datacenter = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/datacenter/{id}")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            datacenter_json = resp.json()
            datacenter = DatacenterSummary(**datacenter_json)
        else:
            resp.raise_for_status()

        return datacenter

    def get_by_name(self, name: str) -> DatacenterSummary:
        """
            Retrieves a datacenter summary by name.

            :param name: Name of the datacenter to find.

            :returns: Matching datacenter summary or ``None``.
            :rtype: DatacenterSummary
        """

        agent = self.agent
        
        dc_summary = None

        datacenter_list = self.list()
        for dcitem in datacenter_list:
            if dcitem.name == name:
                dc_summary = dcitem
                break

        return dc_summary

    def list(self) -> List[DatacenterSummary]:
        """
            Lists the datacenters available on the vSphere server.

            :returns: Collection of datacenter summaries.
            :rtype: List[DatacenterSummary]
        """
        datacenter_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/datacenter")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            found_list = resp.json()
            datacenter_list = [DatacenterSummary(**fitem) for fitem in found_list]
        else:
            resp.raise_for_status()

        return datacenter_list
