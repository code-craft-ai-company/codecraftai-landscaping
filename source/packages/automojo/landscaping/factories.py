
from typing import Generator

from automojo import testbase

from automojo.landscaping.wellknown import LandscapeSingleton
from automojo.landscaping.landscape import Landscape

from automojo.landscaping.clients.linux.linuxclientcoordinatorcoupling import LinuxClientCoordinatorCoupling

@testbase.register.resource_factory()
def create_landscape(constraints={}) -> Generator[Landscape, None, None]:
    lscape = LandscapeSingleton()
    yield lscape

@testbase.register.integration_factory()
def create_linux_client_coordinator_coupling() -> Generator[LinuxClientCoordinatorCoupling, None, None]:
    lc_coupling = LinuxClientCoordinatorCoupling()
    yield lc_coupling
