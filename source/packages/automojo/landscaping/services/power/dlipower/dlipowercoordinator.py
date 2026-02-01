"""
    .. module:: dlipowercoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerCoordinator which is used for managing connectivity with pools of ssh capable devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Union

from automojo.landscaping.services.servicecoordinatorbase import ServiceCoordinatorBase
from automojo.landscaping.landscapeparameters import LandscapeActivationParams
from automojo.landscaping.landscapedevice import LandscapeDevice

class DliPowerCoordinator(ServiceCoordinatorBase):
    """
        The :class:`DliPowerCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

    @property
    def creates_control_points(self) -> bool:
        """
            Property that indicates if the service coordinator creates control points.
        """
        return True

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        self._power_config = {}

        for pcfg in self._coord_config:
            cfgname = pcfg["name"]
            self._power_config[cfgname] = pcfg

        self._power_interfaces = {}

        lscape = self.landscape

        # For DLI Power, we assume standard outlets 1-8 (or as configured)
        # We need to register individual outlets as control points in the operational layer
        for svc in self.children_as_extension:
             # Just a basic loop for standard 8 outlet DLI
             # In a real scenario, we might query the device.
             for outlet_idx in range(1, 9):
                 control_key = f"{svc.host}:outlet:{outlet_idx}"
                 # We register the service under this specific key
                 # The checkout mechanism will look this up.
                 # Note: This requires the operational layer to have a method to add to the pool
                 # Or we can just access the pool if we are in the activate phase?
                 # LandscapeOperationalLayer populates the pool by iterating services.
                 # But it uses service.identity.
                 # We need to change how the pool is populated or add these extra keys.
                 pass

        return

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with devices.
        """
        results = []

        cmd: str = "echo 'It Works'"

        for agent in self.children_as_extension:
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
                device = self._cl_children[host].basedevice
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
                if ip in self._cl_ip_to_host_lookup:
                    host = self._cl_ip_to_host_lookup[ip]
                    if host in self._cl_children:
                        device = self._cl_children[host].basedevice
        finally:
            self._coord_lock.release()

        return device
