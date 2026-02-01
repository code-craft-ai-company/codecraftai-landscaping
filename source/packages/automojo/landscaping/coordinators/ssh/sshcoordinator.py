"""
    .. module:: sshcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the SshPoolCoordinator which is used for managing connectivity with pools of ssh capable devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

import os
import pprint
import weakref

from automojo.errors.exceptions import ConfigurationError
from automojo.interop.protocols.ssh.sshagent import SshAgent

from automojo.landscaping.friendlyidentifier import FriendlyIdentifier
from automojo.landscaping.coordinatorbase import CoordinatorBase
from automojo.landscaping.includefilters import IncludeServiceByName
from automojo.landscaping.landscapeparameters import LandscapeActivationParams
from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.coordinators.ssh.sshdevice import SshDevice
from automojo.landscaping.protocolextensions.sshprotocolextension import SshProtocolExtension

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

INTEGRATION_CLASS_NETWORK_SSH = "network/ssh"

def format_ssh_device_configuration_error(message, sshdev_config):
    """
        Takes an error message and an SSH device configuration info dictionary and
        formats a configuration error message.
    """
    error_lines = [
        message,
        "DEVICE:"
    ]

    dev_repr_lines = pprint.pformat(sshdev_config, indent=4).splitlines(False)
    for dline in dev_repr_lines:
        error_lines.append("    " + dline)
    
    errmsg = os.linesep.join(error_lines)
    return errmsg

class SshCoordinator(CoordinatorBase):
    """
        The :class:`SshPoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        """
            Constructs an instance of the :class:`SshCoordinator`.

            :param lscape: The owning :class:`Landscape` instance.
        """
        super().__init__(lscape, *args, **kwargs)

        self._cl_ip_to_host_lookup: Dict[str, str] = {}
        return

    @property
    def children(self) -> List[SshDevice]:
        """
            Returns a list of the devices created by the coordinator and registered by the coordinator with the Landscape object.
        """
        chlist = super().children
        return chlist

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        lscape = self.landscape

        for device in self.children:
            device.enhance()

            if device.is_configured_for_power:
                power_config = device.device_config["features"]["power"]
                server = power_config["server"]

                service_list = lscape.layer_integration.get_services(include_filters=[IncludeServiceByName(server)])
                if not service_list:
                    errmsg = format_ssh_device_configuration_error(
                        f"The device '{device.host}' is configured for power, but the service '{server}' could not be found.", device.device_config
                    )
                    raise ConfigurationError(errmsg)
        return

    def create_landscape_device(self, landscape: "Landscape", device_info: Dict[str, Any]) -> Tuple[FriendlyIdentifier, SshDevice]:
        """
            Called to declare a declared landscape device for a given coordinator.
        """
        host = device_info["host"]
        dev_type = device_info["deviceType"]
        
        fid = FriendlyIdentifier(host, host)

        device = SshDevice(landscape, self, fid, dev_type, device_info)
        
        coord_ref = weakref.ref(self)
        device_ref = weakref.ref(device)

        users = None
        users_names = device_info.get("users", None)
        if users_names is not None:
            users = landscape.credential_manager.lookup_multiple_credentials(users_names)

        jump = device_info.get("jump", None)
        port = int(device_info.get("port", 22))

        if device.ssh_credential is None:
            errmsg = format_ssh_device_configuration_error(
                f"The device '{host}' must have at least one SSH credential assigned.", device_info
            )
            raise ConfigurationError(errmsg)

        features = device_info.get("features", {})
        if "power" in features:
            power_config = features["power"]
            if "server" not in power_config or "outlet" not in power_config:
                errmsg = format_ssh_device_configuration_error(
                    f"The device '{host}' is configured for power, but the 'server' and 'outlet' must be specified.", device_info
                )
                raise ConfigurationError(errmsg)

        ssh_ext = SshProtocolExtension(host, device.ssh_credential, users=users, port=port, jump=jump)
        ssh_ext.initialize(coord_ref, device_ref, host, host, device_info)
        
        with self.begin_locked_coordinator_scope() as locked:
            self._cl_children[host] = device
            self._cl_ip_to_host_lookup[ssh_ext.ipaddr] = host

        device.attach_extension("network/ssh", ssh_ext)

        return fid, device

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with devices.
        """
        results = []

        cmd: str = "echo 'It Works'"

        for device in self.children:
            agent = device.ssh
            host = agent.host
            ipaddr = agent.ipaddr
            try:
                status, stdout, stderr = agent.run_cmd(cmd)
                results.append((host, ipaddr, status, stdout, stderr, None))
            except Exception as xcpt: # pylint: disable=broad-except
                results.append((host, ipaddr, None, None, None, xcpt))

        return results

    def lookup_device_by_host(self, host: str) -> Union[LandscapeDevice, None]:
        """
            Looks up the agent for a device by its hostname.  If the
            agent is not found then the API returns None.

            :param host: The host name of the LandscapeDevice to search for.

            :returns: The found LandscapeDevice or None
        """
        device = None

        self._coord_lock.acquire()
        try:
            if host in self._cl_children:
                device = self._cl_children[host]
        finally:
            self._coord_lock.release()

        return device

    def lookup_device_by_ip(self, ip) -> Union[LandscapeDevice, None]:
        """
            Looks up the agent for a device by its ip address.  If the
            agent is not found then the API returns None.

            :param ip: The ip address of the LandscapeDevice to search for.

            :returns: The found LandscapeDevice or None
        """
        device = None

        self._coord_lock.acquire()
        try:
            if ip in self._cl_ip_to_host_lookup:
                host = self._cl_ip_to_host_lookup[ip]
                if host in self._cl_children:
                    device = self._cl_children[host]
        finally:
            self._coord_lock.release()

        return device

    def verify_connectivity(self, cmd: str = "echo 'It Works'", user: Optional[str] = None, raiseerror: bool = True) -> List[tuple]:
        """
            Loops through the nodes in the SSH pool and utilizes the credentials for the specified user in order to verify
            connectivity with the remote node.

            :param cmd: A command to run on the remote machine in order
            to verify that ssh connectivity can be establish.
            :param user: The name of the user credentials to use for connectivity.
            If the 'user' parameter is not provided, then the
            credentials of the default or priviledged user will be used.
            :param raiseerror: A boolean value indicating if this API should raise an Exception on failure.

            :returns: A list of errors encountered when verifying connectivity with the devices managed or watched by the coordinator.
        """
        results = []

        for device in self.children:
            agent = device.ssh
            host = agent.host
            ipaddr = agent.ipaddr
            try:
                status, stdout, stderr = agent.run_cmd(cmd, user=user)
                results.append((host, ipaddr, status, stdout, stderr, None))
            except Exception as xcpt: # pylint: disable=broad-except
                if raiseerror:
                    raise
                results.append((host, ipaddr, None, None, None, xcpt))

        return results
