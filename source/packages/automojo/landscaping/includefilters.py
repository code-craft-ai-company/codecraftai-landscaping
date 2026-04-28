"""
    .. module:: includefilters
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing various device include filters.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from abc import abstractmethod
from typing import Any

from automojo.interfaces.iincludefilter import IIncludeFilter

from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.landscapeservice import LandscapeService

class IncludeDeviceBase(IIncludeFilter):
    """
        Marker base class for device-targeted include filters.

        Concrete subclasses must override :meth:`should_include`.  This
        class itself is abstract — direct instantiation produces a
        filter whose ``should_include`` returns ``None`` (because the
        upstream :class:`IIncludeFilter` Protocol declares the method
        without a body), which would silently drop every device from
        the filtered output.  The ``@abstractmethod`` declaration below
        makes that misuse fail loudly at instantiation time instead.
    """

    @abstractmethod
    def should_include(self, check_object: Any) -> bool:
        """
            Override in a concrete subclass.

            :param check_object: The candidate object.
            :returns: ``True`` when the object should be included.
        """

class IncludeDeviceConfigBase(IIncludeFilter):
    """
        Marker base class for device-config-targeted include filters.

        See :class:`IncludeDeviceBase` for the rationale behind the
        abstract :meth:`should_include` declaration.
    """

    @abstractmethod
    def should_include(self, check_object: Any) -> bool:
        """
            Override in a concrete subclass.

            :param check_object: The candidate object.
            :returns: ``True`` when the object should be included.
        """

class IncludeServiceBase(IIncludeFilter):
    """
        Marker base class for service-targeted include filters.

        See :class:`IncludeDeviceBase` for the rationale behind the
        abstract :meth:`should_include` declaration.
    """

    @abstractmethod
    def should_include(self, check_object: Any) -> bool:
        """
            Override in a concrete subclass.

            :param check_object: The candidate object.
            :returns: ``True`` when the object should be included.
        """

class IncludeDeviceByDeviceType(IncludeDeviceBase):
    """
        Includes devices that match a specific device type.
    """

    def __init__(self, device_type: str) -> None:
        """
            Initializes a filter that matches devices by type.

            :param device_type: The device type to include.
        """
        super().__init__()
        self._device_type = device_type
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.device_type == self._device_type:
                include = True

        return include


class IncludeDeviceByDeviceTypeAndRole(IncludeDeviceBase):
    """
        Includes devices that match a device type and role.
    """

    def __init__(self, device_type: str, role: str) -> None:
        """
            Initializes a filter that matches devices by type and role.

            :param device_type: The device type to include.
            :param role: The role the device must match.
        """
        super().__init__()
        self._device_type = device_type
        self._role = role
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.device_type == self._device_type and lsdevice.role == self._role:
                include = True

        return include


class IncludeDeviceByGroup(IncludeDeviceBase):
    """
        Includes devices that are members of a named group.
    """

    def __init__(self, group: str) -> None:
        """
            Initializes a filter that matches devices by group name.

            :param group: The device group label to include.
        """
        super().__init__()
        self._group = group
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.group == self._group:
                include = True

        return include


class IncludeDeviceByName(IncludeDeviceBase):
    """
        Includes devices that match a specific device name.
    """

    def __init__(self, name: str) -> None:
        """
            Initializes a filter that matches devices by name.

            :param name: The device name to include.
        """
        super().__init__()
        self._name = name
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.name == self._name:
                include = True

        return include


class IncludeDeviceByRole(IncludeDeviceBase):
    """
        Includes devices that match a specific role.
    """

    def __init__(self, role: str) -> None:
        """
            Initializes a filter that matches devices by role.

            :param role: The role value to include.
        """
        super().__init__()
        self._role = role
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.role == self._role:
                include = True

        return include


class IncludeDeviceConfigByDeviceType(IncludeDeviceConfigBase):
    """
        Includes device configuration entries that match a device type.
    """

    def __init__(self, device_type: str) -> None:
        """
            Initializes a filter that matches device configuration entries by type.

            :param device_type: The device type to include.
        """
        super().__init__()
        self._device_type = device_type
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device config matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, dict):
            devconfig: dict = check_object
            if devconfig["deviceType"] == self._device_type:
                include = True

        return include

class IncludeServiceByName(IncludeServiceBase):
    """
        Includes services that match a specific service name.
    """

    def __init__(self, name: str) -> None:
        """
            Initializes a filter that matches services by name.

            :param name: The service name to include.
        """
        super().__init__()
        self._name = name
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeService):
            lsdevice: LandscapeService = check_object
            if lsdevice.name == self._name:
                include = True

        return include
