"""
.. module:: windowsclientcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the WindowsPoolCoordinator which is used for managing connectivity with pools of Windows capable devices

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import Any, Dict, Optional, TYPE_CHECKING

from automojo.credentials.basecredential import BaseCredential
from automojo.landscaping.clients.clientcoordinatorbase import ClientCoordinatorBase

from automojo.landscaping.clients.constants import INTEGRATION_CLASS_FOR_WINDOWS_CLIENT
from automojo.landscaping.clients.windows.windowsclient import WindowsClient

from automojo.interop.protocols.ssh.sshagent import SshAgent
from automojo.landscaping.coordinators.integrationclasses import INTEGRATION_CLASS_NETWORK_SSH

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class WindowsClientCoordinator(ClientCoordinatorBase):
    """
        The :class:`WindowsPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Windows
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_WINDOWS_CLIENT
    CLIENT_TYPE = WindowsClient

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return


    def configure_devices(self, landscape: "Landscape") -> list:
        """
            Called by configuration tools running in the "Infrastructure Orchestration" layer to configure
            a coordinator devices.
        """
        results = []

        return results


    def create_ssh_agent(self, device: WindowsClient, device_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        
        ssh_agent = SshAgent(host, cred, users=users, port=port, pty_params=pty_params)

        device.attach_extension(INTEGRATION_CLASS_NETWORK_SSH, ssh_agent)
        return