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
        Specialized :class:`LandscapeDeviceCluster` for Raspberry Pi nodes.
    """

    def __init__(self, label: str, nodes: Dict[str, NodeBase], spares: Dict[str, NodeBase],
                 group: LandscapeDeviceGroup) -> None:
        """
            Constructs a :class:`PiCluster` instance.

            :param label: Name for the cluster.
            :param nodes: Dictionary of active nodes.
            :param spares: Dictionary of spare nodes.
            :param group: Device group associated with the cluster.
        """
        super().__init__(label, nodes, spares, group)
        return
