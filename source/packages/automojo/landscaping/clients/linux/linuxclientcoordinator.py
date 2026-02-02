"""
    .. module:: linuxclientcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the LinuxPoolCoordinator which is used for managing connectivity with pools of LINUX capable devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional, TYPE_CHECKING

import weakref

from automojo.credentials.basecredential import BaseCredential
from automojo.landscaping.clients.clientcoordinatorbase import ClientCoordinatorBase

from automojo.landscaping.clients.constants import INTEGRATION_CLASS_FOR_LINUX_CLIENT
from automojo.landscaping.clients.linux.linuxclient import LinuxClient

from automojo.landscaping.integrationclasses import INTEGRATION_CLASS_NETWORK_SSH
from automojo.landscaping.extensions.protocol.sshprotocolextension import SshProtocolExtension

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class LinuxClientCoordinator(ClientCoordinatorBase):
    """
        The :class:`LinuxClientCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Linux
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_LINUX_CLIENT
    CLIENT_TYPE = LinuxClient

    MUST_INCLUDE_SSH = True

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        """
            Creates a :class:`LinuxClientCoordinator` instance.

            :param lscape: The landscape this coordinator belongs to.
        """
        super().__init__(lscape, *args, **kwargs)
        return


    def configure_devices(self, landscape: "Landscape") -> list:
        """
            Called by configuration tools running in the "Infrastructure Orchestration" layer to configure
            a coordinator devices.
        """
        results = []

        return results


    def create_ssh_agent(self, device: LinuxClient, device_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        """
            Attaches an SSH agent extension to a Linux client.

            :param device: The device instance to attach to.
            :param device_info: Configuration dictionary for the device.
            :param host: Host name of the target device.
            :param cred: SSH credential to use for the connection.
            :param users: Optional user mapping information.
            :param port: SSH port number.
            :param pty_params: Optional pseudo terminal parameters.
        """

        coord_ref = weakref.ref(self)
        device_ref = weakref.ref(device)

        jump = device_info.get("jump", None)

        ssh_ext = SshProtocolExtension(host, cred, users=users, port=port, jump=jump, pty_params=pty_params)
        ssh_ext.initialize(coord_ref, device_ref, host, host, device_info)

        device.attach_extension(INTEGRATION_CLASS_NETWORK_SSH, ssh_ext)
        return