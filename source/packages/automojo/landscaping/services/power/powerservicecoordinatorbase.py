"""
    .. module:: powercoordinatorbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the PowerCoordinatorBase which is used for managing connectivity with pools of power devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Union, TYPE_CHECKING

from automojo.errors.exceptions import ConfigurationError

from automojo.landscaping.services.servicecoordinatorbase import ServiceCoordinatorBase
from automojo.landscaping.landscapeparameters import LandscapeActivationParams
from automojo.landscaping.landscapedevice import LandscapeDevice

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class PowerServiceCoordinatorBase(ServiceCoordinatorBase):
    """
        The :class:`PowerCoordinatorBase` creates a coordinator that can create power service nodes.
    """
    
    POWER_AGENT_TYPE = None

    def __init__(self, lscape: "Landscape", power_interfaces: Dict[str, Any], *args, **kwargs):
        """
            Initializes the coordinator with a mapping of available power interfaces.

            :param lscape: The owning :class:`Landscape` instance.
            :param power_interfaces: Dictionary of power interface objects keyed by name.
        """
        super().__init__(lscape, *args, **kwargs)

        self._power_interfaces = power_interfaces
        return

    @property
    def creates_control_extensions(self) -> bool:
        """
            Property that indicates if the service coordinator creates control extensions.
        """
        return True

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        self._power_config = {}

        for pcfg in self._coord_config:
            cfgname = pcfg["name"]
            self._power_config[cfgname] = pcfg

        return

    def lookup_power_agent(self, power_mapping: Dict[str, Any]):
        """
            Looks up a power agent instance using a mapping that describes
            the interface and switch to control.

            :param power_mapping: Mapping describing the power interface.

            :returns: Instantiated power agent for the given interface.
        """

        power_agent = None

        pname = power_mapping["name"]
        pswitch = power_mapping["switch"]

        power_iface = self._lookup_power_interface(pname)
        if power_iface is not None:
            power_agent = self.POWER_AGENT_TYPE(power_iface, pswitch)
        else:
            errmsg = "Failure to find power interface %r." % pname
            raise ConfigurationError(errmsg) from None

        return power_agent
    
    def _lookup_power_interface(self, name: str) -> Union[LandscapeDevice, None]:
        """
            Called to lookup a power interface by name.
        """
        power_iface = None

        if name in self._power_interfaces:
            power_iface = self._power_interfaces[name]
        else:
            errmsg = "Failure to find power interface %r." % name
            raise ConfigurationError(errmsg) from None

        return power_iface

