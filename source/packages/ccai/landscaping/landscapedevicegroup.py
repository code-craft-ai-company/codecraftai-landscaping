"""
    .. module:: landscapedevicegroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`LandscapeDeviceGroup` object which is a
    container object which groups :class:`Landscapedevice` object with
    thier group name.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import List

import weakref

from ccai.landscaping.landscapedevice import LandscapeDevice

class LandscapeDeviceGroup:
    """
        A :class:`LandscapeDeviceGroup` object is used to group devices to an associated
        grouping label.
    """

    def __init__(self, label: str, items: List[LandscapeDevice]) -> None:
        """
            Constructs a :class:`LandscapeDeviceGroup`.

            :param label: The name assigned to the group.
            :param items: The list of devices that belong to the group.
        """
        self._label = label
        self._items = items
        
        self._coord_ref = weakref.ref(self._items[0].coordinator)
        return
    
    @property
    def coordinator(self):
        """
            Returns the coordinator responsible for devices in this group.
        """
        return self._coord_ref()

    @property
    def items(self):
        """
            Returns the list of devices in the group.
        """
        return self._items

    @property
    def label(self):
        """
            Returns the group label for this collection of devices.
        """
        return self._label
