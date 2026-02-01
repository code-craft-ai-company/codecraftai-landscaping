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

from automojo.landscaping.services.power.powerservicecoordinatorcouplingbase import PowerServiceCoordinatorCouplingBase
from automojo.landscaping.services.power.dlipower.dlipowercoordinator import DliPowerCoordinator
from automojo.landscaping.integrationclasses import INTEGRATION_CLASS_NETWORK_DLIPOWER


# Types imported only for type checking purposes
if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class DLIPowerServiceCoordinatorCoupling(PowerServiceCoordinatorCouplingBase):
    """
        The DLIPowerServiceCoordinatorCoupling handle the requirement registration for the SSH coordinator.
    """

    integration_class: str = INTEGRATION_CLASS_NETWORK_DLIPOWER
    COORDINATOR_TYPE = DliPowerCoordinator

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`DLIPowerServiceCoordinatorCoupling`.
        """
        super().__init__(*args, **kwargs)
        return


