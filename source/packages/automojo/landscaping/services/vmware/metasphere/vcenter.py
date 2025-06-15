"""
    .. module:: vcenter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the vcenter functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from enum import Enum

class FolderType(str, Enum):
    """
        Folder types recognized by vCenter.
    """
    DATACENTER = "DATACENTER"
    DATASTORE = "DATASTORE"
    HOST = "HOST"
    NETWORK = "NETWORK"
    VIRTUAL_MACHINE = "VIRTUAL_MACHINE"

class VmPowerState(str, Enum):
    """
        Power states that a virtual machine can be in.
    """
    POWERED_OFF = "POWERED_OFF"
    POWERED_ON = "POWERED_ON"
    SUSPENDED = "SUSPENDED"
