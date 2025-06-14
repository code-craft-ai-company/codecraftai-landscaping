"""
    .. module:: servicebase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`BaseService` object which is a base
    class for objects that inter-operate with a computer service
    operating system.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import TYPE_CHECKING

from automojo.landscaping.landscapeservice import LandscapeService
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier


if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class ServiceBase(LandscapeService):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, service_type: str, service_config: dict):
        """
            Initializes a :class:`ServiceBase` instance.

            :param lscape: The :class:`Landscape` this service belongs to.
            :param coordinator: Coordinator managing the service.
            :param friendly_id: A :class:`FriendlyIdentifier` for the service.
            :param service_type: The type of service.
            :param service_config: Configuration dictionary for the service.
        """
        super().__init__(lscape, coordinator, friendly_id, service_type, service_config)

        self._host = service_config["host"]
        return

    @property
    def host(self) -> str:
        """
            Returns the host name associated with this service.
        """
        return self._host

    def enhance(self):
        """
            Called to allow a service to enhance its metadata past what is declared in the
            configuration file.  For service that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the service.
        """
        return
