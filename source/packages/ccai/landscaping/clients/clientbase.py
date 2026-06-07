"""
    .. module:: clientbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`BaseClient` object which is a base
    class for objects that inter-operate with a computer client
    operating system.

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

class ClientBase(LandscapeDevice):
    """
        Base class for objects that interact with remote clients.
    """

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initializes a :class:`ClientBase` instance.

            :param lscape: The landscape this client belongs to.
            :param coordinator: Coordinator responsible for the client.
            :param friendly_id: The :class:`FriendlyIdentifier` for the client.
            :param device_type: The declared device type.
            :param device_config: Configuration dictionary for the client.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._host = device_config["host"]
        return

    @property
    def host(self) -> str:
        """
            Returns the host name for the client.
        """
        return self._host

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
