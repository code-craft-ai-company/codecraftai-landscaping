"""
    .. module:: automationpod
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the automationpod functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from automojo.landscaping.wellknown import LandscapeSingleton

from automojo.landscaping.landscape import Landscape
from automojo.testbase.coupling.configurationcoupling import ConfigurationCoupling


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
