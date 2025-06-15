"""
    .. module:: vmext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VmExt object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional, TYPE_CHECKING

from  http import HTTPStatus

from automojo.errors.exceptions import SemanticError

from automojo.landscaping.services.vmware.metasphere.vmguestos import VmGuestOS
from automojo.landscaping.services.vmware.metasphere.vmhardware import VmHardwareVersion
from automojo.landscaping.services.vmware.datastructures.model.vm import VmInfo

from automojo.landscaping.services.vmware.datastructures.model.summary import (
    DatacenterSummary, FolderSummary, VmSummary
)

from automojo.landscaping.services.vmware.datastructures.specs.vmcreate import VmCreateSpec
from automojo.landscaping.services.vmware.datastructures.specs.vmplacement import VmPlacementSpec
from automojo.landscaping.services.vmware.datastructures.specs.vmhardware import (
    VmHardwareBootCreateSpec,
    VmHardwareCpuUpdateSpec,
    VmHardwareDiskCreateSpec,
    VmHardwareFloppyCreateSpec,
    VmHardwareCdromCreateSpec,
    VmHardwareMemoryUpdateSpec,
    VmHardwareEthernetCreateSpec,
    VmHardwareAdapterNvmeCreateSpec,
    VmHardwareParallelCreateSpec,
    VmHardwareBootDeviceEntryCreateSpec,
    VmHardwareAdapterSataCreateSpec,
    VmHardwareAdapterScsiCreateSpec,
    VmHardwareSerialCreateSpec
)
from automojo.landscaping.services.vmware.datastructures.specs.vmstorage import VmStoragePolicySpec


from automojo.landscaping.services.vmware.vsphere.ext.baseext import BaseExt


if TYPE_CHECKING:
    from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent


class VmExt(BaseExt):
    """
        Extension providing VM operations for a vSphere agent.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Creates a VM management extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return

    def create(self, *, guestos: VmGuestOS, placement: Optional[VmPlacementSpec],
               name: Optional[str],
               boot: Optional[VmHardwareBootCreateSpec],
               cpu: Optional[VmHardwareCpuUpdateSpec],
               memory: Optional[VmHardwareMemoryUpdateSpec],
               disks: Optional[List[VmHardwareDiskCreateSpec]],
               nics: Optional[List[VmHardwareEthernetCreateSpec]],
               hardware_version: Optional[VmHardwareVersion],
               floppies: Optional[List[VmHardwareFloppyCreateSpec]],
               cdroms: Optional[List[VmHardwareCdromCreateSpec]],
               nvme_adapters: Optional[List[VmHardwareAdapterNvmeCreateSpec]],
               parallel_ports: Optional[List[VmHardwareParallelCreateSpec]],
               boot_devices: Optional[List[VmHardwareBootDeviceEntryCreateSpec]],
               sata_adapters: Optional[List[VmHardwareAdapterSataCreateSpec]],
               scsi_adapters: Optional[List[VmHardwareAdapterScsiCreateSpec]],
               serial_ports: Optional[List[VmHardwareSerialCreateSpec]],
               storage_policy: Optional[VmStoragePolicySpec]
               ):

        """
            Creates a new virtual machine.

            :param guestos: Guest OS identifier.
            :param placement: Placement specification for the VM.
            :param name: Optional name for the VM.
            :param boot: Optional boot configuration.
            :param cpu: Optional CPU configuration.
            :param memory: Optional memory configuration.
            :param disks: Optional list of disk specifications.
            :param nics: Optional list of network interface specifications.
            :param hardware_version: Optional hardware version.
            :param floppies: Optional floppy device specifications.
            :param cdroms: Optional CD-ROM device specifications.
            :param nvme_adapters: Optional NVMe adapter specifications.
            :param parallel_ports: Optional parallel port specifications.
            :param boot_devices: Optional boot device list.
            :param sata_adapters: Optional SATA adapter specifications.
            :param scsi_adapters: Optional SCSI adapter specifications.
            :param serial_ports: Optional serial port specifications.
            :param storage_policy: Optional storage policy specification.

            :returns: :class:`VmInfo` describing the created VM.
            :rtype: VmInfo
        """

        agent = self.agent

        if placement is None:
            if not agent.filter_state.has_working_placement():
                errmsg = "If a placement specificate is not passed, then " \
                    "one must be actively applied before trying to create a VM."
                raise SemanticError(errmsg)
        
            placement = agent.filter_state.working_placement

        createSpec = VmCreateSpec(guest_OS=guestos, placement=placement, name=name, boot=boot, cpu=cpu,
                                  memory=memory, disks=disks, nics=nics, hardware_version=hardware_version,
                                  floppies=floppies, cdroms=cdroms, nvme_adapters=nvme_adapters,
                                  parallel_ports=parallel_ports, boot_devices=boot_devices, sata_adapters=sata_adapters,
                                  scsi_adapters=scsi_adapters, serial_ports=serial_ports, storage_policy=storage_policy)
        

        payload = createSpec.asdict()

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, data=payload, action="clone")
        if resp.status_code == HTTPStatus.OK:
            vminfo_dict = resp.json()
            vminfo = VmInfo.from_dict(vminfo_dict)
        else:
            resp.raise_for_status()

        return vminfo

    def clone(self, source: str, name: str, power_on: bool=False, customizations: Optional[dict]=None,
              parentfolder: Optional[FolderSummary] = None) -> str:

        """
            Clones an existing virtual machine.

            :param source: Identifier of the source VM.
            :param name: Name for the new VM.
            :param power_on: ``True`` to power on after clone.
            :param customizations: Optional customization spec.
            :param parentfolder: Optional target folder for the clone.

            :returns: Identifier of the cloned VM.
            :rtype: str
        """

        vm_id = None

        agent = self.agent

        placement = {}

        if parentfolder is not None:
            placement["folder"] = parentfolder.folder
        elif agent.filter_state.has_working_folder_filter:
            placement["folder"] = agent.filter_state.working_folder.folder

        body = {
            "name": name,
            "source": source,
            "power_on": power_on,
            "placement": placement
        }

        if customizations is not None:
            body.update(customizations)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, params={"action": "clone"})
        if resp.status_code == HTTPStatus.OK:
            vm_id = resp.json()
        else:
            resp.raise_for_status()

        return vm_id

    def delete(self, id: str):
        """
            Deletes a VM from vCenter inventory.

            :param id: Identifier of the VM to delete.
        """

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/vm/{id}")

        resp = agent.session_delete(req_url)
        if resp.status_code != HTTPStatus.OK:
            resp.raise_for_status()

        return

    def get(self, id: str) -> VmInfo:
        """
            Retrieves information about a VM.

            :param id: Identifier of the VM to retrieve.

            :returns: :class:`VmInfo` for the VM.
            :rtype: VmInfo
        """

        vminfo = None

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/vm/{id}")

        resp = agent.session_get(req_url)
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
            vminfo = VmInfo.from_dict(vminfo)

        else:
            resp.raise_for_status()

        return vminfo

    def get_summary_by_name(self, name: str) -> VmSummary:
        """
            Retrieves a VM summary by name.

            :param name: Name of the VM to search for.

            :returns: Matching :class:`VmSummary` or ``None``.
            :rtype: VmSummary
        """

        vm_summary = None

        vm_list = self.list()
        for vmitem in vm_list:
            if vmitem.name == name:
                vm_summary = vmitem
                break

        return vm_summary

    def list(self, *, datacenters: Optional[List[DatacenterSummary]]=None, parentfolders: Optional[List[FolderSummary]]=None) -> List[VmSummary]:
        """
            Lists virtual machines with optional filters.

            :param datacenters: Optional datacenter filter list.
            :param parentfolders: Optional parent folder filter list.

            :returns: List of VM summaries.
            :rtype: List[VmSummary]
        """

        vm_list = None

        agent = self.agent

        req_url = agent.build_api_url("/vcenter/vm")
        
        params = {}
        if datacenters is not None:
            filter_datacenters = [ dc.datacenter for dc in datacenters]
            params['datacenters'] = filter_datacenters
        elif agent.filter_state.has_working_datacenter_filter:
            filter_datacenters = [agent.filter_state.working_datacenter.datacenter]
            params['datacenters'] = filter_datacenters

        if parentfolders is not None:
            filter_parent_folders = [ pf.folder for pf in parentfolders ]
            params['folders'] = filter_parent_folders
        elif agent.filter_state.has_working_folder_filter:
            filter_parent_folders = [ agent.filter_state.working_folder.folder ]
            params['folders'] = filter_parent_folders

        resp = agent.session_get(req_url, params=params)

        if resp.status_code == HTTPStatus.OK:
            vm_json_list = resp.json()
            vm_list = [VmSummary(**vmitem) for vmitem in vm_json_list]
        else:
            resp.raise_for_status()

        return vm_list

    def register(self, name: str, storage: dict, placement: Optional[dict]=None):
        """
            Registers an existing VM with vCenter.

            :param name: Name of the VM to register.
            :param storage: Dictionary describing the VM storage.
            :param placement: Optional placement specification.

            :returns: Result dictionary from the register operation.
        """

        vminfo = None

        agent = self.agent

        body = {
            "name": name,
        }
        body.update(storage)

        if placement is not None:
            body.update(placement)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, action="register")
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo
    
    def relocate(self, path: str, disks: Optional[dict]=None, placement: Optional[dict]=None):
        """
            Relocates a VM's configuration or disks.

            :param path: New datastore path for the VM.
            :param disks: Optional disk relocation specification.
            :param placement: Optional placement specification.

            :returns: Result dictionary from the relocate operation.
        """

        vminfo = None

        agent = self.agent

        body = {
            "path": path,
        }
        
        if disks is not None:
            body["disks"] = disks

        if placement is not None:
            body.update(placement)

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, json=body, action="relocate")
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return vminfo

    def unregister(self, vmid: str):
        """
            Unregisters a VM from vCenter.

            :param vmid: Identifier of the VM to unregister.
        """

        agent = self.agent

        req_url = agent.build_api_url(f"/vcenter/vm")

        resp = agent.session_post(req_url, action="unregister", vm=vmid)
        if resp.status_code == HTTPStatus.OK:
            vminfo = resp.json()
        else:
            resp.raise_for_status()

        return
