"""
    .. module:: tcpserialcoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TcpSerialCoordinator which is used for managing connectivity with pools of tcp serial devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Tuple, Union, TYPE_CHECKING

import weakref

from ccai.landscaping.coordinatorbase import CoordinatorBase
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier
from ccai.landscaping.landscapeparameters import LandscapeActivationParams
from ccai.landscaping.landscapedevice import LandscapeDevice
from ccai.landscaping.coordinators.serial.tcp.tcpserialdevice import TcpSerialDevice

from ccai.landscaping.extensions.protocol.tcpserialprotocolextension import TcpSerialProtocolExtension

if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape

class TcpSerialCoordinator(CoordinatorBase):
    """
        The :class:`TcpSerialCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        """
            Constructs a new :class:`TcpSerialCoordinator` instance.

            :param lscape: The owning :class:`Landscape`.
        """
        super().__init__(lscape, *args, **kwargs)

        self._cl_ip_to_host_lookup: Dict[str, str] = {}
        return

    @property
    def creates_control_extensions(self) -> bool:
        """
            Returns a boolean indicating if this coordinator creates control extensions.
        """
        return True

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        for device in self.children:
            device.enhance()
        return

    def get_control_extensions(self) -> List[Tuple[str, Any]]:
        """
            Returns a list of control extensions managed by this coordinator.
        """
        extensions = []

        for device in self.children:
            # We want to expose the serial extension of this device
            if hasattr(device, "serial"):
                ext = device.serial

                dev_config = device.device_config
                host = dev_config["host"]

                # Ensure port is treated as an integer for key generation consistency
                port = int(dev_config["port"])

                key = f"serial: host={repr(host)} port={repr(port)}"
                extensions.append((key, ext))

        return extensions

    def create_landscape_device(self, landscape: "Landscape", device_info: Dict[str, Any]) -> Tuple[FriendlyIdentifier, TcpSerialDevice]:
        """
            Called to declare a declared landscape device for a given coordinator.
        """
        host = device_info["host"]
        port = int(device_info["port"])

        dev_type = None
        if "deviceType" in device_info:
            dev_type = device_info["deviceType"]
        elif "serialType" in device_info:
            dev_type = device_info["serialType"]

        fid = FriendlyIdentifier(host, host)

        device = TcpSerialDevice(landscape, self, fid, dev_type, device_info)
        
        coord_ref = weakref.ref(self)
        device_ref = weakref.ref(device)

        serial_ext = TcpSerialProtocolExtension(host, port=port)
        serial_ext.initialize(coord_ref, device_ref, host, host, device_info)

        with self.begin_locked_coordinator_scope() as locked:
            self._cl_children[host] = device
            self._cl_ip_to_host_lookup[device.ipaddr] = host

        device.attach_extension("serial", serial_ext)

        return fid, device

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with devices.
        """
        results = []

        cmd: str = "echo 'It Works'"

        for device in self.children:
            agent = device.serial
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
