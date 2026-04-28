"""
    .. module:: dlipowerprotocolextension
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the DliPowerProtocolExtension functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional

import weakref

from automojo.credentials.basiccredential import BasicCredential

from automojo.landscaping.extensions.control.controlextension import ControlExtension

from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient
from automojo.interop.protocols.power.dlipower.dlipoweroutletcontrol import DliPowerOutletControl
from automojo.landscaping.extensions.protocol.protocolextension import ProtocolExtension

class DliPowerControlExtension(DliPowerOutletControl, ProtocolExtension, ControlExtension):
    """
        DLI Power agent integrated as a control extension for a landscape device.
    """

    def __init__(self, client: DliPowerRestClient, outlet_index: int):
        """
            Constructs an :class:`DliPowerControlExtension` instance.

            :param client: The DliPowerRestClient instance used for communication.
            :param outlet_index: The index of the outlet to control.
        """
        DliPowerOutletControl.__init__(self, client, outlet_index)
        ProtocolExtension.__init__(self)
        ControlExtension.__init__(self)
        return
    
    def initialize(self, coord_ref: weakref.ReferenceType, basedevice_ref: weakref.ReferenceType, extid: str, location: str, configinfo: dict, **kwargs):
        """
            Initializes the landscape device extension. It is not required to call this function in order to use a DliPowerOutletControl, it is used
            when an outlet is attached to a LandscapeDevice as a device extension.

            Because :class:`DliPowerControlExtension` inherits from BOTH
            :class:`ProtocolExtension` (the device-side surface) and
            :class:`ControlExtension` (the service-side surface), this
            method seeds both sets of bookkeeping fields.  Without the
            second initialise call, the ``service`` / ``control_id`` /
            ``control_info`` accessors inherited from
            :class:`ControlExtension` would resolve to ``None`` even after
            the extension was nominally initialised, breaking any consumer
            that reaches the control surface.

            :param coord_ref: A weak reference to the coordinator that is
                              managing interactions through this device
                              extension.  This same reference is used as
                              the ``service_ref`` on the control surface
                              because the coordinator is the producer of
                              the underlying service.
            :param basedevice_ref: A weak reference to the
                                   :class:`LandscapeDevice` this extension
                                   is attached to (``None`` until attach).
            :param extid: A unique reference that can be used to identify
                          this device via the coordinator.  Re-used as the
                          control identifier on the control surface.
            :param location: The location reference where this device can
                             be found via the coordinator.
            :param configinfo: The configuration information dictionary.
                               Re-used as ``control_info`` on the control
                               surface.
            :param kwargs: Protocol-specific extra initialization data
                           forwarded to :class:`ProtocolExtension`.
        """
        ProtocolExtension.initialize(self, coord_ref, basedevice_ref, extid, location, configinfo, **kwargs)
        ControlExtension.initialize(self, coord_ref, basedevice_ref, extid, configinfo)
        return
