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
        """
            Returns a strong reference to the :class:`LandscapeDevice` this
            control extension is attached to, or ``None`` when the extension
            has not yet been bound (the canonical state immediately after
            ``__init__``) or when the underlying weak reference has been
            collected.
        """
        dev = None
        if self._extends_ref is not None:
            dev = self._extends_ref()
        return dev

    @property
    def service(self) -> "ServiceBase":
        """
            Returns a strong reference to the :class:`ServiceBase` this
            control extension is associated with, or ``None`` when the
            extension has not yet been bound or when the underlying weak
            reference has been collected.
        """
        svc = None
        if self._service_ref is not None:
            svc = self._service_ref()
        return svc

    def initialize(self, service_ref: weakref.ReferenceType, extends_ref: weakref.ReferenceType,
                   control_id: str, control_info: dict) -> None:
        """
            Initializes the landscape device control extension.

            :param service_ref: Weak reference to the owning :class:`ServiceBase`.
            :param extends_ref: Weak reference to the :class:`LandscapeDevice`
                                this control point extends.
            :param control_id: Stable identifier for this control point.
            :param control_info: Configuration dict for this control point.
        """
        self._service_ref = service_ref
        self._extends_ref = extends_ref
        self._control_id = control_id
        self._control_info = control_info
        return

    def update_extends_ref(self, extends_ref: weakref.ReferenceType) -> None:
        """
            Updates the :class:`LandscapeDevice` weak reference after the
            control extension has been pre-created (e.g. by a service
            coordinator before any device is known to be associated).  This
            mirrors :meth:`ProtocolExtension.update_extends_ref` so pure
            :class:`ControlExtension` subclasses (i.e. those that do NOT
            also inherit from :class:`ProtocolExtension`) can be wired up
            uniformly.

            :param extends_ref: Weak reference to the device this control
                                point now extends.
        """
        self._extends_ref = extends_ref
        return

    def update_service_ref(self, service_ref: weakref.ReferenceType) -> None:
        """
            Updates the :class:`ServiceBase` weak reference after the
            control extension has been pre-created.  Symmetric counterpart
            to :meth:`update_extends_ref`.

            :param service_ref: Weak reference to the owning service.
        """
        self._service_ref = service_ref
        return