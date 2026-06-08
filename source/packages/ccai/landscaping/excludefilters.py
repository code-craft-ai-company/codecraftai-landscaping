"""
    .. module:: excludefilters
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing various device exclude filters.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from abc import abstractmethod
from typing import Any

from ccai.interfaces.iexcludefilter import IExcludeFilter

from ccai.landscaping.landscapedevice import LandscapeDevice
from ccai.landscaping.landscapeservice import LandscapeService

class ExcludeDeviceBase(IExcludeFilter):
    """
        Marker base class for device-targeted exclude filters.

        Concrete subclasses must override :meth:`should_exclude`.  This
        class itself is abstract — direct instantiation produces a
        filter whose ``should_exclude`` returns ``None`` (because the
        upstream :class:`IExcludeFilter` Protocol declares the method
        without a body), which would silently keep every device in
        the filtered output.  The ``@abstractmethod`` declaration below
        makes that misuse fail loudly at instantiation time instead.
    """

    @abstractmethod
    def should_exclude(self, check_object: Any) -> bool:
        """
            Override in a concrete subclass.

            :param check_object: The candidate object.
            :returns: ``True`` when the object should be excluded.
        """

class ExcludeDeviceConfigBase(IExcludeFilter):
    """
        Marker base class for device-config-targeted exclude filters.

        See :class:`ExcludeDeviceBase` for the rationale behind the
        abstract :meth:`should_exclude` declaration.
    """

    @abstractmethod
    def should_exclude(self, check_object: Any) -> bool:
        """
            Override in a concrete subclass.

            :param check_object: The candidate object.
            :returns: ``True`` when the object should be excluded.
        """

class ExcludeServiceBase(IExcludeFilter):
    """
        Marker base class for service-targeted exclude filters.

        See :class:`ExcludeDeviceBase` for the rationale behind the
        abstract :meth:`should_exclude` declaration.
    """

    @abstractmethod
    def should_exclude(self, check_object: Any) -> bool:
        """
            Override in a concrete subclass.

            :param check_object: The candidate object.
            :returns: ``True`` when the object should be excluded.
        """

class ExcludeDeviceByDeviceType(ExcludeDeviceBase):
    """
        Excludes devices that match a specific device type.
    """

    def __init__(self, device_type: str) -> None:
        """
            Initializes a filter that matches devices by type.

            :param device_type: The device type to exclude.
        """
        super().__init__()
        self._device_type = device_type
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.device_type == self._device_type:
                exclude = True

        return exclude


class ExcludeDeviceByDeviceTypeAndRole(ExcludeDeviceBase):
    """
        Excludes devices that match a device type and role.
    """

    def __init__(self, device_type: str, role: str) -> None:
        """
            Initializes a filter that matches devices by type and role.

            :param device_type: The device type to exclude.
            :param role: The role the device must match.
        """
        super().__init__()
        self._device_type = device_type
        self._role = role
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.device_type == self._device_type and lsdevice.role == self._role:
                exclude = True

        return exclude


class ExcludeDeviceByGroup(ExcludeDeviceBase):
    """
        Excludes devices that are members of a named group.
    """

    def __init__(self, group: str) -> None:
        """
            Initializes a filter that matches devices by group name.

            :param group: The device group label to exclude.
        """
        super().__init__()
        self._group = group
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.group == self._group:
                exclude = True

        return exclude


class ExcludeDeviceByName(ExcludeDeviceBase):
    """
        Excludes devices that match a specific device name.
    """

    def __init__(self, name: str) -> None:
        """
            Initializes a filter that matches devices by name.

            :param name: The device name to exclude.
        """
        super().__init__()
        self._name = name
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.name == self._name:
                exclude = True

        return exclude


class ExcludeDeviceByRole(ExcludeDeviceBase):
    """
        Excludes devices that match a specific role.
    """

    def __init__(self, role: str) -> None:
        """
            Initializes a filter that matches devices by role.

            :param role: The role value to exclude.
        """
        super().__init__()
        self._role = role
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.role == self._role:
                exclude = True

        return exclude


class ExcludeDeviceConfigByDeviceType(ExcludeDeviceConfigBase):
    """
        Excludes device configuration entries that match a device type.
    """

    def __init__(self, device_type: str) -> None:
        """
            Initializes a filter that matches device configuration entries by type.

            :param device_type: The device type to exclude.
        """
        super().__init__()
        self._device_type = device_type
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device config matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, dict):
            devconfig: dict = check_object
            if devconfig["deviceType"] == self._device_type:
                exclude = True

        return exclude

class ExcludeServiceByName(ExcludeServiceBase):
    """
        Excludes services that match a specific service name.
    """

    def __init__(self, name: str) -> None:
        """
            Initializes a filter that matches services by name.

            :param name: The service name to exclude.
        """
        super().__init__()
        self._name = name
        return

    def should_exclude(self, check_object: Any) -> bool:
        """
            Determines if a device matches an exclude criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        exclude = False

        if isinstance(check_object, LandscapeService):
            lsdevice: LandscapeService = check_object
            if lsdevice.name == self._name:
                exclude = True

        return exclude
