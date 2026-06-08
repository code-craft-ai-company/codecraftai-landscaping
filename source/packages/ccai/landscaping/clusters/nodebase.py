"""
    .. module:: nodebase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`BaseNode` object which is a base
    class for objects that inter-operate with a compute cluster
    node.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import TYPE_CHECKING

from ccai.landscaping.landscapedevice import LandscapeDevice
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier

if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape
    from ccai.landscaping.coordinatorbase import CoordinatorBase

class NodeBase(LandscapeDevice):
    """
        Base class representing a node that belongs to a compute cluster.
    """

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Constructs a :class:`NodeBase` instance.

            :param lscape: The :class:`Landscape` this node belongs to.
            :param coordinator: Coordinator managing the node.
            :param friendly_id: Friendly identifier for the node.
            :param device_type: The device type of the node.
            :param device_config: Configuration dictionary for the node.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._name = device_config["name"]
        self._host = device_config["host"]
        return

    @property
    def name(self) -> str:
        """
            The configured name of the node.
        """
        return self._name

    @property
    def host(self) -> str:
        """
            The host name or IP address of the node.
        """
        return self._host

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
