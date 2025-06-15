"""
    .. module:: folderext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the FolderExt object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional, TYPE_CHECKING

from  http import HTTPStatus

from automojo.landscaping.services.vmware.datastructures.vcenter import (
    DatacenterSummary, FolderSummary
)

from automojo.landscaping.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent

class FolderExt(BaseExt):
    """
        Extension that handles folder-related actions in vSphere.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Creates the folder extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
    
    def find_descendant(self, folder_leaf_names: List[str]):
        """
            Traverses descendant folders to find a specific folder.

            :param folder_leaf_names: Ordered list of folder leaf names.

            :returns: Folder summary if found.
            :rtype: FolderSummary
        """

        agent = self.agent

        search_leaves = [lf for lf in folder_leaf_names]

        filter_datacenters = [agent.filter_state.working_datacenter]

        found = None
        nxtfound = None

        parentFolders = []
        while True:
            nxtleaf = folder_leaf_names.pop(0)

            folders = self.list(datacenters=filter_datacenters, parentfolders=parentFolders)
            for fitem in folders:
                if fitem.name == nxtleaf:
                    nxtfound = fitem
                    break

            if len(folder_leaf_names) > 0:
                parentFolders = [nxtfound]
            else:
                found = nxtfound
                break
    
        return found

    def list(self, *, datacenters: Optional[List[DatacenterSummary]]=None, parentfolders: Optional[List[FolderSummary]]=None) -> List[FolderSummary]:
        """
            Retrieves a list of folders based on optional filters.

            :param datacenters: Optional list of datacenters to filter on.
            :param parentfolders: Optional list of parent folders to filter on.

            :returns: Collection of folder summaries.
            :rtype: List[FolderSummary]
        """
        folder_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/folder")

        params = {}
        if datacenters is not None:
            filter_datacenters = [ dc.datacenter for dc in datacenters]
            params['datacenters'] = filter_datacenters
        elif agent.filter_state.has_working_datacenter_filter:
            filter_datacenters = [agent.filter_state.working_datacenter.datacenter]
            params['datacenters'] = filter_datacenters

        if parentfolders is not None:
            filter_parent_folders = [ pf.folder for pf in parentfolders ]
            params['parent_folders'] = filter_parent_folders
        elif agent.filter_state.has_working_folder_filter:
            filter_parent_folders = [ agent.filter_state.working_folder.folder ]
            params['parent_folders'] = filter_parent_folders

        resp = agent.session_get(req_url, params=params)

        if resp.status_code == HTTPStatus.OK:
            found_list = resp.json()

            folder_list = [FolderSummary(**fitem) for fitem in found_list]
        else:
            resp.raise_for_status()

        return folder_list
