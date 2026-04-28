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

from automojo.errors.exceptions import SemanticError

from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier

from automojo.interop.protocols.serial.tcpserialagent import TcpSerialAgent

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinatorbase import CoordinatorBase

# Canonical extension key for the TCP-serial protocol extension.  Centralised
# here so the producer side and the consumer side cannot drift apart.
_SERIAL_EXTENSION_KEY = "serial"


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

            :raises SemanticError: When no serial extension has been attached to this
                                   device.  This indicates API misuse — either the
                                   coordinator failed to attach the extension during
                                   landscape activation, or a caller is using a device
                                   that was never wired for TCP serial.
        """
        if _SERIAL_EXTENSION_KEY not in self._extensions:
            err_msg_lines = [
                "No TCP serial extension is attached to this device.",
                "    DEVICE: {}".format(self._friendly_id.full_identifier),
                "    EXPECTED EXTENSION KEY: {}".format(_SERIAL_EXTENSION_KEY),
                "    ATTACHED EXTENSION KEYS: {}".format(sorted(self._extensions.keys())),
            ]
            err_msg = "\n".join(err_msg_lines)
            raise SemanticError(err_msg)
        ext = self._extensions[_SERIAL_EXTENSION_KEY]
        return ext

