

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
