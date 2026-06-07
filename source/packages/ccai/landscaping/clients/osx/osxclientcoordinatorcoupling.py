"""
    .. module:: osxclientcoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a OsxClientCoordinatorCoupling object to use for working with the OSX clients.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from ccai.landscaping.clients.clientcoordinatorcouplingbase import ClientCoordinatorCouplingBase

from ccai.landscaping.clients.constants import INTEGRATION_CLASS_FOR_OSX_CLIENT
from ccai.landscaping.clients.osx.osxclientcoordinator import OsxClientCoordinator


class OsxClientCoordinatorCoupling(ClientCoordinatorCouplingBase):
    """
        The OsxClientCoordinatorCoupling handle the requirement registration for the OSX coordinator.
    """

    COORDINATOR_TYPE = OsxClientCoordinator

    integration_root: str = "apod"
    integration_section: str = "clients"
    integration_leaf: str = "deviceType"
    integration_class: str = INTEGRATION_CLASS_FOR_OSX_CLIENT

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`OsxCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return
