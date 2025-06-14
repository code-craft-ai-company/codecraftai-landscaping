"""
    .. module:: pinodecoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the PiNodeCoordinator which is used for managing connectivity with raspberry
    pi computer nodes in a raspberry pi cluster.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import Any, Dict, Optional, TYPE_CHECKING

from automojo.credentials.basecredential import BaseCredential
from automojo.landscaping.clusters.nodecoordinatorbase import NodeCoordinatorBase

from automojo.landscaping.clusters.constants import INTEGRATION_CLASS_FOR_RASPBERRYPI_NODE
from automojo.landscaping.clusters.raspberrypi.pinode import PiNode
from automojo.landscaping.clusters.raspberrypi.picluster import PiCluster

from automojo.interop.protocols.ssh.sshagent import SshAgent
from automojo.landscaping.coordinators.ssh.sshcoordinator import INTEGRATION_CLASS_NETWORK_SSH

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class PiNodeCoordinator(NodeCoordinatorBase):
    """
        The :class:`LinuxPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote Linux
        client.
    """

    INTEGRATION_CLASS = INTEGRATION_CLASS_FOR_RASPBERRYPI_NODE
    CLIENT_TYPE = PiNode
    CLUSTER_TYPE = PiCluster

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return

    def create_ssh_agent(self, device: PiNode, device_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        
        ssh_agent = SshAgent(host, cred, users=users, port=port, pty_params=pty_params)

        device.attach_extension(INTEGRATION_CLASS_NETWORK_SSH, ssh_agent)
        return