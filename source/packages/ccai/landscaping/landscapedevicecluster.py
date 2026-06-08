"""
    .. module:: landscapedevicecluster
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`LandscapeDeviceCluster` object which 
    represents a cluster of devices that are compute nodes in a
    computer or storage cluster.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import Dict

from ccai.landscaping.clusters.nodebase import NodeBase
from ccai.landscaping.landscapedevicegroup import LandscapeDeviceGroup

class LandscapeDeviceCluster:
    """
        A :class:`LandscapeDeviceCluster` object is used to manage a group of
        nodes that are part of a computer cluster and a collection of spares
        that are eligible to participate in the cluster.
    """

    def __init__(self, name: str, nodes: Dict[str, NodeBase], spares: Dict[str, NodeBase],
                 group: LandscapeDeviceGroup) -> None:
        """
            Initializes a :class:`LandscapeDeviceCluster` instance.

            :param name: Name of the cluster.
            :param nodes: Mapping of node names to node objects.
            :param spares: Mapping of spare node names to node objects.
            :param group: Device group associated with the cluster.
        """
        self._name = name
        self._nodes = nodes
        self._spares = spares
        self._group = group
        return

    @property
    def group(self) -> LandscapeDeviceGroup:
        """
            Returns the device group associated with this cluster.
        """
        return self._group

    @property
    def name(self) -> str:
        """
            Returns the name assigned to this cluster.
        """
        return self._name

    @property
    def nodes(self) -> Dict[str, NodeBase]:
        """
            Returns a mapping of node names to node devices.
        """
        return self._nodes
    
    @property
    def spares(self) -> Dict[str, NodeBase]:
        """
            Returns a mapping of spare node names to node devices.
        """
        return self._spares

    def enhance_metadata(self):
        """
            Hook function to allow a cluster object the opportunity to enhance its Metadata.
        """
        return
