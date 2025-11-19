"""
    .. module:: powercoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a PowerCoordinatorCoupling object to use for working with standard
    power agent types.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from automojo.landscaping.coordinators.power.powercoordinatorcouplingbase import PowerCoordinatorCouplingBase
from automojo.landscaping.integrationclasses import INTEGRATION_CLASS_NETWORK_DLIPOWER


# Types imported only for type checking purposes
if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

def is_dlipower_type(config_info) -> bool:
    """
        Checks if the provided configuration describes a DLI power device.

        :param config_info: Dictionary of power configuration values.

        :returns: ``True`` if the configuration matches the DLI power type.
    """

    is_sst = False

    if "powerType" in config_info:
        stval = config_info["powerType"]
        if stval == INTEGRATION_CLASS_NETWORK_DLIPOWER:
            is_sst = True

    return is_sst

class DLIPowerCoordinatorCoupling(PowerCoordinatorCouplingBase):
    """
        The DLIPowerCoordinatorCoupling handle the requirement registration for the SSH coordinator.
    """

    integration_class: str = INTEGRATION_CLASS_NETWORK_DLIPOWER

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`DLIPowerCoordinatorCoupling`.
        """
        super().__init__(*args, **kwargs)
        return

    @classmethod
    def attach_to_environment(cls, landscape: "Landscape"):
        """
            This API is called so that the IntegrationCoupling can process configuration information.  The :class:`IntegrationCoupling`
            will verify that it has a valid environment and configuration to run in.

            :raises :class:`automojo.errors.exceptions.ConfigurationError`:
        """

        cls.landscape = landscape
        layer_config = landscape.layer_configuration

        power_list = layer_config.get_power_configs()
        if len(power_list) > 0:
            supported_power_list = [pconf for pconf in filter(is_dlipower_type, power_list)]

            if len(supported_power_list) > 0:
                layer_integ = landscape.layer_integration
                layer_integ.register_integration_dependency(cls)

        return


