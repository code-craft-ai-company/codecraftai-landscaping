"""
    .. module:: picluster
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the PiCluster object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Dict

from automojo.landscaping.clusters.nodebase import NodeBase
from automojo.landscaping.landscapedevicecluster import LandscapeDeviceCluster
from automojo.landscaping.landscapedevicegroup import LandscapeDeviceGroup

class PiCluster(LandscapeDeviceCluster):
    """
    """

    def __init__(self, label: str, nodes: Dict[str, NodeBase], spares: Dict[str, NodeBase],
                 group: LandscapeDeviceGroup) -> None:
        super().__init__(label, nodes, spares, group)
        return
