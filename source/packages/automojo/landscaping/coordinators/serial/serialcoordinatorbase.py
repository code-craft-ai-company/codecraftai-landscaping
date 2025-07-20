"""
    .. module:: tcpserialcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TcpSerialCoordinator which is used for managing connectivity with pools of tcp serial devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Union, TYPE_CHECKING

from automojo.errors.exceptions import ConfigurationError

from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
from automojo.landscaping.landscapeparameters import LandscapeActivationParams
from automojo.landscaping.landscapedevice import LandscapeDevice


if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class SerialCoordinatorBase(CoordinatorBase):
    """
        The :class:`TcpSerialCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

    SERIAL_AGENT_TYPE = None

    def __init__(self, lscape: "Landscape", serial_interfaces: Dict[str, Any], *args, **kwargs):
        """
            Initializes the coordinator with a dictionary of serial
            interfaces that can be used to create serial agents.

            :param lscape: The owning :class:`Landscape` instance.
            :param serial_interfaces: Mapping of serial interface objects by name.
        """
        super().__init__(lscape, *args, **kwargs)
        self._serial_interfaces = serial_interfaces
        return

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        self._serial_config = {}

        for pcfg in self._coord_config:
            cfgname = pcfg["name"]
            self._serial_config[cfgname] = pcfg

        return

    def lookup_serial_agent(self, serial_mapping: Dict[str, Any]):
        """
            Creates a serial agent instance based on the provided mapping.

            :param serial_mapping: Dictionary describing the serial interface.

            :returns: Instantiated serial agent for the requested interface.
        """

        serial_agent = None

        sername = serial_mapping["name"]
        socket = serial_mapping["socket"]

        serial_iface = self._lookup_serial_interface(sername)
        if serial_iface is not None:
            serial_agent = self.SERIAL_AGENT_TYPE(serial_iface, socket)
        else:
            errmsg = "Failure to find serial interface %r." % sername
            raise ConfigurationError(errmsg) from None

        return serial_agent
    
    def _lookup_serial_interface(self, name: str) -> Union[LandscapeDevice, None]:
        """
            Called to lookup a serial interface by name.
        """
        serial_iface = None

        if name in self._serial_interfaces:
            serial_iface = self._serial_interfaces[name]
        else:
            errmsg = "Failure to find power interface %r." % name
            raise ConfigurationError(errmsg) from None

        return serial_iface