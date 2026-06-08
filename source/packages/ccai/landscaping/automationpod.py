"""
    .. module:: automationpod
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the automationpod functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from ccai.landscaping.wellknown import LandscapeSingleton

from ccai.landscaping.landscape import Landscape
from ccai.testbase.coupling.configurationcoupling import ConfigurationCoupling


class AutomationPod(ConfigurationCoupling):
    """
        The :class:`AutomationPod` class provides access to the global
        :class:`Landscape` instance used by automation pods.
    """

    def __init__(self):
        """
            Creates a new :class:`AutomationPod` instance.
        """
        self._lscape = LandscapeSingleton()
        return
    
    @property
    def landscape(self) -> Landscape:
        """
            Returns the global :class:`Landscape` instance used by this
            automation pod.
        """
        return self._lscape
