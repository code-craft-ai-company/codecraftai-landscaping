"""
    .. module:: tcpserialdevice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TcpSerialDevice object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import TYPE_CHECKING

from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier

from automojo.interop.protocols.serial.tcpserialagent import TcpSerialAgent

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class TcpSerialDevice(LandscapeDevice):
    """
        Represents a serial device that communicates over TCP.
    """

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initializes a :class:`TcpSerialDevice` instance.

            :param lscape: The landscape this device belongs to.
            :param coordinator: Coordinator managing the device.
            :param friendly_id: Friendly identifier for the device.
            :param device_type: Declared device type.
            :param device_config: Configuration dictionary for the device.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._host = device_config["host"]
        self._port = device_config["port"]
        return

    @property
    def host(self) -> str:
        """
            Host name or IP address of the device.
        """
        return self._host

    @property
    def port(self) -> int:
        """
            TCP port used to connect to the device.
        """
        return self._port

    @property
    def serial(self) -> TcpSerialAgent:
        """
            Returns the :class:`TcpSerialAgent` extension for this device.
        """
        ext = self._extensions["network/ssh"]
        return ext

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
