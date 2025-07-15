"""
    .. module:: extensionpoints
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing functions and classes that help create and work with
    configuration based extension objects.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import List, Protocol, Type

from automojo.extension.factory.factoryprotocolbase import FactoryProtocolBase
from automojo.testbase.coupling.integrationcoupling import IntegrationCoupling

class LandscapingFactoryProtocol(FactoryProtocolBase):
    """
        Protocol defining extension points for landscaping integrations.
    """

    factory_protocol_name = "mojo-landscaping-extension-protocol"

    @classmethod
    def get_landscape_type(self) -> Type:
        """
            Used to lookup and return the most relevant `Landscape` type.
        """

    @classmethod
    def get_integration_coupling_types(self) -> List[Type[IntegrationCoupling]]:
        """
            Used to lookup and return the most relevant list of integration coupling types.
        """

    

