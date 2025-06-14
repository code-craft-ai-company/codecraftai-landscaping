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
        The :class:`AutomationPodBase` object serves as a base class for derived :class:`AutomationPodBase` objects.
    """

    def __init__(self):
        self._lscape = LandscapeSingleton()
        return
    
    @property
    def landscape(self) -> Landscape:
        return self._lscape
