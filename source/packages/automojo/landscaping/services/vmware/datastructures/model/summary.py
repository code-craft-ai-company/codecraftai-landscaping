
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from dataclasses import dataclass

from automojo.landscaping.services.vmware.metasphere.vcenter import FolderType
from automojo.landscaping.services.vmware.metasphere.vcenter import VmPowerState

@dataclass
class DatacenterSummary:
    name: str
    datacenter: str

@dataclass
class FolderSummary:
    name: str
    folder: str
    type: FolderType

@dataclass
class VmSummary:
    name: str
    power_state: VmPowerState
    vm: str
    cpu_count: int
    memory_size_MiB: int
