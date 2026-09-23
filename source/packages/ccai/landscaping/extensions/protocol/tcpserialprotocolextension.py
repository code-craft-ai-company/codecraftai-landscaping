"""
    .. module:: tcpserialprotocolextension
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the TcpSerialProtocolExtension functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Optional

import weakref

from ccai.landscaping.extensions.control.controlextension import ControlExtension
from ccai.landscaping.extensions.protocol.protocolextension import ProtocolExtension

from ccai.interop.aspects import AspectsCmd, DEFAULT_CMD_ASPECTS

from ccai.interop.protocols.serial.tcpserialagent import TcpSerialAgent

class TcpSerialProtocolExtension(TcpSerialAgent, ProtocolExtension, ControlExtension):
    """
        Serial agent integrated as a protocol extension for a landscape device.
    """

    def __init__(self, host: str, port: int, called_id: Optional[str]=None, aspects: AspectsCmd = DEFAULT_CMD_ASPECTS):
        """
            Constructs an :class:`TcpSerialProtocolExtension` instance.

            :param host: Host name or IP address for the TCP serial port connection.
            :param port: TCP serial port to connect to.
            :param called_id: Identifier used when logging sessions.
            :param aspects: Command aspects controlling execution behavior.
        """
        # TcpSerialAgent.__init__ signature might have changed in interop package.
        # Removing called_id to fix TypeError.
        TcpSerialAgent.__init__(self, host, port, aspects=aspects)
        ProtocolExtension.__init__(self)
        ControlExtension.__init__(self)
        return
    
    def initialize(self, coord_ref: weakref.ReferenceType, basedevice_ref: weakref.ReferenceType, extid: str, location: str, configinfo: dict, **kwargs):
        """
            Initializes the landscape device extension. It is not required to call this function in order to use an TcpSerialAgent, it is used
            when an agent is attached to a LandscapeDevice as a device extension.

            Because :class:`TcpSerialProtocolExtension` inherits from BOTH
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
                              the ``service_ref`` on the control surface.
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
