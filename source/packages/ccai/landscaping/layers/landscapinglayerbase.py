"""
    .. module:: landscapeintegrationlayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeLayerBase` class which is used
    to provide common functionality to the different landscape layers.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import TYPE_CHECKING

from ccai.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import weakref

if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape


class LandscapingLayerBase:
    """
        Base class providing common functionality for landscape layers.
    """

    logger = getEnhancedLogger()

    def __init__(self, lscape: "Landscape"):
        """
            Initializes a :class:`LandscapingLayerBase` instance.

            :param lscape: The owning :class:`Landscape` object.
        """
        self._lscape_ref = weakref.ref(lscape)
        return

    @property
    def landscape(self):
        """
            Returns a strong reference to the :class:`Landscape` instance.
        """
        lscape = self._lscape_ref()
        return lscape
