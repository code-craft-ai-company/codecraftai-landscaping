"""
    .. module:: dlipowercoordinator
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerCoordinator which is used for managing connectivity with pools of ssh capable devices

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Tuple, Union
import weakref

from automojo.landscaping.services.servicecoordinatorbase import ServiceCoordinatorBase
from automojo.landscaping.landscapeparameters import LandscapeActivationParams
from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.extensions.control.controlextension import ControlExtension
from automojo.landscaping.extensions.control.dlipowercontrolextension import DliPowerControlExtension
from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class DliPowerCoordinator(ServiceCoordinatorBase):
    """
        The :class:`DliPowerCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote SSH
        nodes.
    """
    # pylint: disable=attribute-defined-outside-init

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

        for svc in self.children:
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

                # Create the shared client for this service
                client = DliPowerRestClient(host, credential, port=port)

                # For DLI Power, typically 8 outlets.
                # In robust implementation, this might be configurable per device.
                for outlet_idx in range(1, 9):
                    # control_key format: "power: outlet={outlet_idx} server='{host}'"
                    # keys are sorted: outlet, server
                    control_key = f"power: outlet={outlet_idx} server='{host}'"

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

        # DLI Power services don't support generic command execution via run_cmd.
        # Connectivity verification should ideally happen via REST client, but here we iterate over services.
        for svc in self.children:
            host = svc.host
            # Placeholder for connectivity check
            results.append((host, None, True, "Connectivity assumed", None, None))

        return results

