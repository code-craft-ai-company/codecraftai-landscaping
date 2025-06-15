"""
    .. module:: summary
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the summary functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from dataclasses import dataclass

from automojo.landscaping.services.vmware.metasphere.vcenter import FolderType
from automojo.landscaping.services.vmware.metasphere.vcenter import VmPowerState

@dataclass
class DatacenterSummary:
    """
        Simple datacenter summary returned from vCenter queries.
    """
    name: str
    datacenter: str

@dataclass
class FolderSummary:
    """
        Folder summary describing a vCenter folder object.
    """
    name: str
    folder: str
    type: FolderType

@dataclass
class VmSummary:
    """
        Summary information about a virtual machine.
    """
    name: str
    power_state: VmPowerState
    vm: str
    cpu_count: int
    memory_size_MiB: int
