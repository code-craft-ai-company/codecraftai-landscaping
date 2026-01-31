"""
    .. module:: sshprotocolextension
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the sshprotocolextension functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional, Union

import socket
import weakref

from automojo.errors.exceptions import ConfigurationError

from automojo.landscaping.protocolextensions.protocolextension import ProtocolExtension

from automojo.credentials.sshcredential import SshCredential

from automojo.interop.aspects import AspectsCmd, DEFAULT_CMD_ASPECTS
from automojo.interop.protocols.ssh.sshagent import SshAgent
from automojo.interop.protocols.ssh.sshconst import SshJumpParams

class SshProtocolExtension(SshAgent, ProtocolExtension):
    """
        SSH agent integrated as a protocol extension for a landscape device.
    """

    def __init__(self, host: str, primary_credential: SshCredential, users: Optional[dict] = None, port: int = 22,
                 jump: Union[str, SshJumpParams, None] = None, pty_params: Optional[dict] = None, called_id: Optional[str]=None,
                 look_for_keys: bool = False, aspects: AspectsCmd = DEFAULT_CMD_ASPECTS):
        """
            Constructs an :class:`SshProtocolExtension` instance.

            :param host: Host name or IP address for the SSH connection.
            :param primary_credential: Primary credential used for authentication.
            :param users: Optional dictionary of additional users.
            :param port: SSH port to connect to.
            :param jump: Jump host or parameters.
            :param pty_params: Optional PTY parameters.
            :param called_id: Identifier used when logging sessions.
            :param look_for_keys: Indicates if agent keys should be used.
            :param aspects: Command aspects controlling execution behavior.
        """
        try:
            SshAgent.__init__(self, host, primary_credential, users=users, port=port, jump=jump, pty_params=pty_params,
                              called_id=called_id, look_for_keys=look_for_keys, aspects=aspects)
        except (socket.gaierror, OSError) as exc:
            errmsg = f"Error initializing SshProtocolExtension for host={host}: {exc}"
            raise ConfigurationError(errmsg) from exc

        ProtocolExtension.__init__(self)
        return
    
    def initialize(self, coord_ref: weakref.ReferenceType, basedevice_ref: weakref.ReferenceType, extid: str, location: str, configinfo: dict):
        """
            Initializes the landscape device extension. It is not required to call this function in order to use an SSHAgent, it is used
            when an agent is attached to a LandscapeDevice as a device extension.

            :param coord_ref: A weak reference to the coordinator that is managing interactions through this
            device extension.
            :param extid: A unique reference that can be used to identify this device via the coordinator even if its location changes.
            :param location: The location reference where this device can be found via the coordinator.
            :param configinfo: The configuration information dictionary from the landscape file for the specified host.
        """
        ProtocolExtension.initialize(self, coord_ref, basedevice_ref, extid, location, configinfo)
        return
