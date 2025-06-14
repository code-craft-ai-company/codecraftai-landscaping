"""
    .. module:: constants
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the constants associated with automation landscaping.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import platform

from enum import Enum, IntEnum

class DeviceExtensionType(str, Enum):
    """
        Enumeration of extension types for landscape devices.
    """

    SSH = "extension/ssh"
    UPNP = "extension/upnp"
    REST = "extension/rest"

class StartupLevel(IntEnum):
    """
        Ordering levels used to sequence device startup.
    """

    Power = 10000
    Serial = 20000
    SecondaryProtocol = 30000
    PrimaryProtocol = 40000

class UPNP_HEADERS:
    """
        HTTP header defaults used for UPNP requests.
    """

    USER_AGENT = "AutomationMojo/1.0 UPNP Test Package"
    SERVER = "{},{},AutomationKit/1.0".format(platform.system(), platform.release())

