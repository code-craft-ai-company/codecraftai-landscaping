"""
    .. module:: isoext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the IsoExt object.

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

class IsoExt(BaseExt):

    def __init__(self, agent: "VSphereAgent"):
        """
            Initializes the ISO extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return
    
    def mount(self, vm: str, library_item: str):
        """
            Mounts an ISO image to a virtual machine.

            :param vm: Identifier of the VM.
            :param library_item: Content library item representing the ISO.

            :returns: Result dictionary from the mount operation.
        """
        result = None

        agent = self.agent

        body = {
            "vm": vm,
            "library_item": library_item
        }

        req_url = agent.build_api_url("/vcenter/iso/image")
        resp = agent.session_post(req_url, json=body, action="mount")

        if resp.status_code == HTTPStatus.OK:
            result = resp.json()
        else:
            resp.raise_for_status()

        return result
    
    def unmount(self, vm: str, cdrom: str):
        """
            Unmounts an ISO image from a virtual machine.

            :param vm: Identifier of the VM.
            :param cdrom: Identifier of the CD-ROM device.

            :returns: Result dictionary from the unmount operation.
        """
        result = None

        agent = self.agent

        body = {
            "vm": vm,
            "cdrom": cdrom
        }

        req_url = agent.build_api_url("/vcenter/iso/image")
        resp = agent.session_post(req_url, json=body, action="unmount")

        if resp.status_code == HTTPStatus.OK:
            result = resp.json()
        else:
            resp.raise_for_status()

        return result