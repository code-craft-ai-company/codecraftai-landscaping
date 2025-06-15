"""
    .. module:: vcenter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the vcenter functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from dataclasses import dataclass

from automojo.landscaping.services.vmware.metasphere.vcenter import FolderType

@dataclass
class DatacenterSummary:
    """
        Summary information describing a datacenter object.
    """
    name: str
    datacenter: str

@dataclass
class FolderSummary:
    """
        Summary describing a folder object in vCenter.
    """
    name: str
    folder: str
    type: FolderType
