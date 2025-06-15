"""
    .. module:: datastoreext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DataStoreExt object.

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

class DataStoreExt(BaseExt):
    """
        Provides datastore operations for a vSphere agent.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the datastore extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
    
    def get(self, name: str):
        """
            Retrieves information about a datastore.

            :param name: Name of the datastore to retrieve.

            :returns: Datastore information dictionary.
        """

        dsinfo = None

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/datastore/{name}")

        resp = agent.session_get(req_url)
        if resp.status_code == HTTPStatus.OK:
            dsinfo = resp.json()
        else:
            resp.raise_for_status()

        return dsinfo

    def list(self):
        """
            Retrieves a list of datastores from vCenter.

            :returns: List of datastore records.
        """
        datastore_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/datastore")
        resp = agent.session_get(req_url)

        if resp.status_code == HTTPStatus.OK:
            datastore_list = resp.json()
        else:
            resp.raise_for_status()

        return datastore_list
