"""
    .. module:: dlipowercoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerCoordinator which is used for managing connectivity with pools of ssh capable devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import socket
from typing import List, Tuple, Union
import weakref

from ccai.landscaping.services.servicecoordinatorbase import ServiceCoordinatorBase
from ccai.landscaping.landscapeparameters import LandscapeActivationParams
from ccai.landscaping.landscapedevice import LandscapeDevice
from ccai.landscaping.extensions.control.controlextension import ControlExtension
from ccai.landscaping.extensions.control.dlipowercontrolextension import DliPowerControlExtension
from ccai.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class DliPowerCoordinator(ServiceCoordinatorBase):
    """
        The :class:`DliPowerCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        """
            Constructs a new :class:`DliPowerCoordinator` instance.
        """
        super().__init__(lscape, *args, **kwargs)
        self._cl_control_extensions = {}
        return

    @property
    def creates_control_extensions(self) -> bool:
        """
            Property that indicates if the service coordinator creates control extensions.
        """
        return True

    def get_control_extensions(self) -> List[Tuple[str, ControlExtension]]:
        """
            Returns a list of control extensions managed by this coordinator.
        """
        extensions = []

        with self.begin_locked_coordinator_scope():
            for svc in self._cl_children.values():
                host = svc.host

                credential = None
                for cred in svc.credentials.values():
                    if "basic" in cred.categories:
                        credential = cred
                        break

                if credential:
                    port = 80
                    if "port" in svc.service_config:
                        port = svc.service_config["port"]

                    client = None

                    # For DLI Power, typically 8 outlets.
                    # In robust implementation, this might be configurable per device.
                    for outlet_idx in range(1, 9):
                        # control_key format: "power: outlet={outlet_idx} server='{host}'"
                        # keys are sorted: outlet, server
                        control_key = f"power: outlet={outlet_idx} server={repr(host)}"

                        if control_key in self._cl_control_extensions:
                            ext = self._cl_control_extensions[control_key]
                            extensions.append((control_key, ext))
                        else:
                            if client is None:
                                # Create the shared client for this service
                                client = DliPowerRestClient(host, credential, port=port)

                            ext = DliPowerControlExtension(client, outlet_idx)

                            coord_ref = weakref.ref(self)

                            # Pre-initialize with service info
                            # Note: basedevice_ref is None until attached to a device
                            ext.initialize(
                                coord_ref,
                                None,
                                "power",
                                host,
                                {"server": host, "outlet": outlet_idx}
                            )

                            self._cl_control_extensions[control_key] = ext
                            extensions.append((control_key, ext))
                else:
                    # Log warning?
                    pass

        return extensions

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        self._power_config = {}

        if self._coord_config is not None:
            for pcfg in self._coord_config:
                cfgname = pcfg["name"]
                self._power_config[cfgname] = pcfg

        self._power_interfaces = {}

        return

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with devices.
        """
        results = []

        for svc in self.children:
            host = svc.host
            ipaddr = svc.ipaddr

            port = 80
            if "port" in svc.service_config:
                port = int(svc.service_config["port"])

            try:
                # Basic TCP connectivity check
                with socket.create_connection((ipaddr, port), timeout=5):
                    pass
                results.append((host, ipaddr, True, "Connectivity established (TCP)", None, None))
            except Exception as xcpt:
                results.append((host, ipaddr, False, None, None, xcpt))

        return results

