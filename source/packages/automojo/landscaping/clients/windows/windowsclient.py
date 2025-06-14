"""
    .. module:: windowsclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the WindowsClient object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import TYPE_CHECKING

from automojo.interop.interfaces.isystemcontext import ISystemContext
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier
from automojo.landscaping.clients.clientbase import ClientBase

from automojo.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class WindowsClient(ClientBase):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initializes a :class:`WindowsClient` instance.

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