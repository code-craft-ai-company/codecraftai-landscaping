"""
    .. module:: wellknown
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the wellknown functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import TYPE_CHECKING

from threading import RLock

from automojo.presence.wellknown import ConfiguredSuperFactorySingleton

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

LANDSCAPE_SINGLETON = None

SINGLETON_LOCK = RLock()

def LandscapeSingleton() -> "Landscape":
    """
        Instantiates and gets a global instance of the :class:`Landscape` class.  The
        :class:`Landscape` provides for management of resources.
    """

    global SINGLETON_LOCK
    global LANDSCAPE_SINGLETON

    # If the singleton is already set, don't bother grabbing a lock
    # to set it.  The full path of the setting of the singleton will only
    # ever be taken once
    if LANDSCAPE_SINGLETON is None:
        super_factory = ConfiguredSuperFactorySingleton()

        SINGLETON_LOCK.acquire()
        try:
            from automojo.landscaping.landscapingfactoryprotocol import LandscapingFactoryProtocol

            if LANDSCAPE_SINGLETON is None:
                LandscapeType = super_factory.get_override_types_by_order(
                    LandscapingFactoryProtocol.get_landscape_type)

                if LandscapeType is None:
                    from automojo.landscaping.landscape import Landscape
                    LandscapeType = Landscape

                LANDSCAPE_SINGLETON = LandscapeType()
        finally:
            SINGLETON_LOCK.release()

    return LANDSCAPE_SINGLETON

