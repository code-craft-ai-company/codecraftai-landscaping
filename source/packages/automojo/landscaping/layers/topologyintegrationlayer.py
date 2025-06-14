"""
    .. module:: topologyintegrationlayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TopologyItegrationLayer` class which is used
    to load initialize the test landscape and integrate with all the available
    landscape resources.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import TYPE_CHECKING

from automojo.landscaping.layers.landscapinglayerbase import LandscapingLayerBase


if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape


class TopologyIntegrationLayer(LandscapingLayerBase):

    def __init__(self, lscape: "Landscape"):
        """
            Creates a :class:`TopologyIntegrationLayer` instance.

            :param lscape: The owning :class:`Landscape` object.
        """
        super().__init__(lscape)
        return
