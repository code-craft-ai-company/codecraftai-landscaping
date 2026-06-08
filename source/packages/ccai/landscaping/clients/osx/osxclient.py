"""
    .. module:: osxclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the OsxClient object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import TYPE_CHECKING

from ccai.interop.interfaces.isystemcontext import ISystemContext
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier
from ccai.landscaping.clients.clientbase import ClientBase

from ccai.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape
    from ccai.landscaping.coordinatorbase import CoordinatorBase

class OsxClient(ClientBase):
    """
        Client implementation for hosts running macOS.
    """

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initializes an :class:`OsxClient` instance.

            :param lscape: The landscape this client belongs to.
            :param coordinator: The coordinator managing this client.
            :param friendly_id: Identifier associated with the client.
            :param device_type: The declared device type.
            :param device_config: Configuration dictionary for the client.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)
        return

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
