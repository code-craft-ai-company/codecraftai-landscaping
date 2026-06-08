"""
    .. module:: linuxclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the LinuxClient object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import TYPE_CHECKING

import shlex

from ccai.credentials.basiccredential import BasicCredential
from ccai.errors.exceptions import CommandError
from ccai.interop.interfaces.isystemcontext import ISystemContext
from ccai.interop.protocols.ssh.sshsession import SshSession
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier
from ccai.landscaping.clients.clientbase import ClientBase

from ccai.landscaping.clients.linux.ext.commandsext import CommandsExt
from ccai.landscaping.clients.linux.ext.configureext import ConfigureExt

from ccai.interop.protocols.ssh.sshagent import SshAgent


if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape
    from ccai.landscaping.coordinatorbase import CoordinatorBase

class LinuxClient(ClientBase):
    """
        Client implementation for hosts running the Linux OS.
    """

    EXT_COMMANDS = CommandsExt
    EXT_CONFIGURE = ConfigureExt

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initializes a :class:`LinuxClient` instance.

            :param lscape: The landscape this client belongs to.
            :param coordinator: Coordinator managing this client.
            :param friendly_id: Identifier associated with the client.
            :param device_type: The declared device type.
            :param device_config: Configuration dictionary for the client.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._ext_commands = self.EXT_COMMANDS(self)
        self._ext_configure = self.EXT_CONFIGURE(self)
        return

    @property
    def commands(self) -> CommandsExt:
        """
            Returns the commands extension for this client.
        """
        return self._ext_commands
    
    @property
    def configure(self) -> ConfigureExt:
        """
            Returns the configuration extension for this client.
        """
        return self._ext_configure

    @property
    def ssh(self) -> SshAgent:
        """
            Returns the SSH agent extension for this client.
        """
        sshagent = self._extensions["network/ssh"]
        return sshagent

    def get_default_system_context(self) -> ISystemContext:
        """
            Called to get an ISystemContext instance that is a default system type.
        """
        return self.ssh

    def open_sudo_ssh_session(self, credential: BasicCredential) -> SshSession:
        """
            Opens an SSH session with sudo privileges authenticated.

            :param credential: The credential to use for sudo authentication.
        """

        session = self.ssh.open_session()

        try:
            password = credential.password
            
            # Use shlex.quote to prevent command injection
            quoted_password = shlex.quote(password)

            # sudo -v updates the user's cached credentials.
            # We quote the password to handle spaces and special characters.
            cmd = f"printf '%s\\n' {quoted_password} | sudo -S -v"
            status, stdout, stderr = session.run_cmd(cmd)

            if status != 0:
                errmsg = f"Failed to authenticate sudo session."
                raise CommandError(errmsg, status, stdout, stderr)

        except Exception:
            session.close()
            raise

        return session
