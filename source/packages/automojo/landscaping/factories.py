"""
    .. module:: factories
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the factories functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Generator

from automojo import testbase

from automojo.landscaping.wellknown import LandscapeSingleton
from automojo.landscaping.landscape import Landscape

from automojo.landscaping.clients.linux.linuxclientcoordinatorcoupling import LinuxClientCoordinatorCoupling

@testbase.register.resource_factory()
def create_landscape(constraints={}) -> Generator[Landscape, None, None]:
    """
        Creates the global :class:`Landscape` instance.

        :param constraints: Optional dictionary of constraints used while constructing the Landscape.

        :returns: A generator yielding the Landscape object.
    """
    lscape = LandscapeSingleton()
    yield lscape

@testbase.register.integration_factory()
def create_linux_client_coordinator_coupling() -> Generator[LinuxClientCoordinatorCoupling, None, None]:
    """
        Creates a :class:`LinuxClientCoordinatorCoupling` instance.

        :returns: A generator yielding the coupling instance.
    """
    lc_coupling = LinuxClientCoordinatorCoupling()
    yield lc_coupling
