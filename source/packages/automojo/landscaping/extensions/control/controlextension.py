"""
    .. module:: controlextension
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`ControlExtension` class which is used to attached control
               capability to a :class:`LandscapeDevice` that is linked to a :class:`LandscapeService`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Dict, Union, TYPE_CHECKING

from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import weakref

if TYPE_CHECKING:
    from automojo.landscaping.services.servicecoordinatorbase import ServiceCoordinatorBase
    from automojo.landscaping.services.servicebase import ServiceBase
    from automojo.landscaping.landscapedevice import LandscapeDevice
    from automojo.landscaping.landscapeservice import LandscapeService

class ControlExtension:
    """
        The :class:`ControlExtension` object is the base class object that allows for addition of controls to extend the functionality
        of  a :class:`LandscapeDevice`.  The :class:`ControlExtension` is used by the various services to link controls back to services.
    """

    logger = getEnhancedLogger()

    def __init__(self):
        """
            Constructor use to create an instance of and to initialize a :class:`ProtocolExtension`.
        """
        self._service_ref = None
        self._extends_ref = None
        self._control_id = None
        self._control_info = None
        self._extid = None
        self._location = None

        return
    
    @property
    def control_id(self) -> str:
        return self._control_id

    @property
    def control_info(self) -> dict:
        return self._control_info

    @property
    def extends(self) -> "LandscapeDevice":
        obj = self._extends_ref()
        return obj

    @property
    def service(self) -> "ServiceBase":
        obj = self._service_ref()
        return obj
    
    def initialize(self, service_ref: weakref.ReferenceType, extends_ref: weakref.ReferenceType,
                   control_id: str, control_info: dict) -> None:
        """
            Initializes the landscape device control extension.
        """
        self._service_ref = service_ref
        self._extends_ref = extends_ref
        self._control_id = control_id
        self._control_info = control_info
        return