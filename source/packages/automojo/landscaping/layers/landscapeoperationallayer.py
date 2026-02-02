"""
    .. module:: landscapeoperationallayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the landscapeoperationallayer functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

import os

from automojo.errors.xtraceback import format_exception
from automojo.errors.exceptions import CheckinError, CheckoutError

from automojo.interfaces.iexcludefilter import IExcludeFilter
from automojo.interfaces.iincludefilter import IIncludeFilter

from automojo.landscaping.layers.landscapinglayerbase import LandscapingLayerBase
from automojo.landscaping.layers.landscapeintegrationlayer import LandscapeIntegrationLayer
from automojo.landscaping.extensions.control.controlextension import ControlExtension
from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.landscapedevicecluster import LandscapeDeviceCluster
from automojo.landscaping.landscapeservice import LandscapeService
from automojo.landscaping.clusters.nodecoordinatorbase import NodeCoordinatorBase

from automojo.landscaping.landscapeparameters import (
    LandscapeActivationParams,
    DEFAULT_LANDSCAPE_ACTIVATION_PARAMS,
)

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape


class LandscapeOperationalLayer(LandscapingLayerBase):
    """
        Layer that manages operational state for landscape devices.  This layer operationalizes
        the devices, services and controls.  This layer also initiates first contact with the
        devices and services and validates that the configuration "contact" information provided
        is valid and devices can be contacted.
    """

    def __init__(self, lscape: "Landscape"):
        """
            Creates a :class:`LandscapeOperationalLayer` instance.

            :param lscape: The owning :class:`Landscape` object.
        """
        super().__init__(lscape)

        self._operational_clusters: Dict[str, LandscapeDeviceCluster] = {}

        self._operational_clusters_pool: Dict[str, LandscapeDeviceCluster] = {}
        self._operational_clusters_outstanding: Dict[str, LandscapeDeviceCluster] = {}

        self._operational_device_pool: Dict[str, LandscapeDevice] = {}
        self._operational_device_outstanding: Dict[str, LandscapeDevice] = {}

        self._operational_controlpoint_pool: Dict[str, ControlExtension] = {}
        self._operational_controlpoint_outstanding: Dict[str, ControlExtension] = {}

        return

    @property
    def available_clusters(self) -> Dict[str, LandscapeDeviceCluster]:
        """
            Provides a thread safe copy of clusters available for checkout.
        """
        cluster_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cluster_table = self._operational_clusters_pool.copy()
        
        return cluster_table

    @property
    def available_devices(self) -> Dict[str, LandscapeDevice]:
        """
            Provides a thread safe copy of devices available for checkout.
        """
        device_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            device_table = self._operational_device_pool.copy()
        
        return device_table

    @property
    def available_control_points(self) -> Dict[str, ControlExtension]:
        """
            Provides a thread safe copy of control points available for checkout.
        """
        service_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            service_table = self._operational_controlpoint_pool.copy()

        return service_table

    @property
    def operational_clusters(self) -> Dict[str, LandscapeDeviceCluster]:
        """
            Provides a thread safe copy of the operational clusters table.
        """
        cluster_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cluster_table = self._operational_clusters.copy()
        
        return cluster_table

    def activate_coordinators(self, activation_params: LandscapeActivationParams):
        """
            Activates the coordinators by having them scan for devices in order to enhance the
            devices.
        """
        lscape = self.landscape

        layer_integ = lscape.layer_integration

        coordinators_for_services = layer_integ.coordinators_for_services
        for coord in coordinators_for_services.values():
            coord.activate(activation_params)

        coordinators_for_power = layer_integ.coordinators_for_power
        for coord in coordinators_for_power.values():
            coord.activate(activation_params)

        coordinators_for_serial = layer_integ.coordinators_for_serial
        for coord in coordinators_for_serial.values():
            coord.activate(activation_params)

        self._initialize_operational_pools()

        for device in self.available_devices.values():
            if device.is_configured_for_power:
                device.attach_to_power()

            if device.is_configured_for_serial:
                device.attach_to_serial()

        coordinators_for_devices = layer_integ.coordinators_for_devices
        for coord in coordinators_for_devices.values():
            coord.activate(activation_params)

        self.establish_connectivity(activation_params)

        return
    
    def checkin_cluster(self, cluster: LandscapeDeviceCluster):
        """
            Checkin clusters and associated devices to the operational pool.
        """

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cname = cluster.name

            if cname not in self._operational_clusters_outstanding:
                err_msg_lines = [
                    f"Checkin of cluster '{cname}' that was not previously checked out."
                    "AVAILABLE POOL:"
                ]

                cluster_name_list = [ncname for ncname in self._operational_clusters_pool.keys()]
                cluster_name_list.sort()
                for ncname in cluster_name_list:
                    err_msg_lines.append(f"    {ncname}")

                err_msg_lines.append("OUTSTANDING POOL:")
                cluster_name_list = [ncname for ncname in self._operational_clusters_outstanding.keys()]
                cluster_name_list.sort()
                for ncname in cluster_name_list:
                    err_msg_lines.append(f"    {ncname}")

                err_msg = os.linesep.join(err_msg_lines)
                raise CheckinError(err_msg)
        
            for node in cluster.nodes.values():
                did = node.identity
                del self._operational_device_outstanding[did]
                self._operational_device_pool[did] = node

            del self._operational_clusters_outstanding[cname]
            self._operational_clusters_pool[cname] = cluster
            
        return

    def checkin_device(self, device: LandscapeDevice):
        """
            Checkin devices to the operational pool.
        """
        
        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            dev_identity = device.identity

            if dev_identity not in self._operational_device_outstanding:
                err_msg_lines = [
                    f"Checkin of device '{dev_identity}' that was not previously checked out."
                    "AVAILABLE POOL:"
                ]

                device_identity_list = [did for did in self._operational_device_pool.keys()]
                device_identity_list.sort()
                for did in device_identity_list:
                    err_msg_lines.append(f"    {did}")

                err_msg_lines.append("OUTSTANDING POOL:")
                device_identity_list = [did for did in self._operational_device_outstanding.keys()]
                device_identity_list.sort()
                for did in device_identity_list:
                    err_msg_lines.append(f"    {did}")

                err_msg = os.linesep.join(err_msg_lines)
                raise CheckinError(err_msg)
            
            del self._operational_device_outstanding[dev_identity]
            self._operational_device_pool[dev_identity] = device

        return

    def checkin_control_point(self, extension: ControlExtension, control_key: str):
        """
            Checkin control point (extension) to the operational pool.
        """

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            if control_key not in self._operational_controlpoint_outstanding:
                err_msg_lines = [
                    f"Checkin of control point '{control_key}' that was not previously checked out."
                    "AVAILABLE POOL:"
                ]

                service_identity_list = [did for did in self._operational_controlpoint_pool.keys()]
                service_identity_list.sort()
                for did in service_identity_list:
                    err_msg_lines.append(f"    {did}")

                err_msg_lines.append("OUTSTANDING POOL:")
                service_identity_list = [did for did in self._operational_controlpoint_outstanding.keys()]
                service_identity_list.sort()
                for did in service_identity_list:
                    err_msg_lines.append(f"    {did}")

                err_msg = os.linesep.join(err_msg_lines)
                raise CheckinError(err_msg)

            del self._operational_controlpoint_outstanding[control_key]
            self._operational_controlpoint_pool[control_key] = extension

        return

    def checkout_cluster(self, cluster: LandscapeDeviceCluster):
        """
            Checkout clusters and associated devices from the operational pool.
        """

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cname = cluster.name
            if cname not in self._operational_clusters:
                err_msg_lines = [
                    f"The cluster named '{cname}' does not exist.",
                    "EXISTING:"
                ]

                for exnames in self._operational_clusters:
                    err_msg_lines.append(f"    {exnames}")

                err_msg = os.linesep.join(err_msg_lines)
                raise CheckoutError(err_msg)
            
            if cname not in self._operational_clusters_pool:
                if cname not in self._operational_clusters_outstanding:
                    err_msg = f"The specified cluster '{cname}' was not found in the pool or outstanding clusters."
                    raise CheckoutError(err_msg)

                # Trying to checkout a cluster that has already been checked out
                err_msg = f"The specified cluster '{cname}' has already been checked out of the pool."
                raise CheckoutError(err_msg)

            # When we checkout a cluster, we have to make sure all of its devices
            # are available for checkout
            unavailable_nodes = []
            for node in cluster.nodes.values():
                node_identity = node.identity
                if node_identity not in self._operational_device_pool:
                    unavailable_nodes.append(node)

            if len(unavailable_nodes) > 0:
                err_msg_lines = [
                    f"Not all of the nodes are available for cluster '{cname}'.",
                    "UNAVAILABLE NODES:"
                ]
                for node in unavailable_nodes:
                    err_msg_lines.append(f"    {node.name}")
                err_msg = os.linesep.join(err_msg_lines)
                raise CheckoutError(err_msg)

            # The cluster is available and all the devices are available, complete the checkout
            for node in cluster.nodes.values():
                node_identity = node.identity

                del self._operational_device_pool[node_identity]
                self._operational_device_outstanding[node_identity] = node

            del self._operational_clusters_pool[cname]
            self._operational_clusters_outstanding[cname] = cluster

        return

    def checkout_device(self, device: LandscapeDevice):
        """
            Checkout devices from the operational pool.
        """
        
        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:

            device_identity = device.identity

            if device_identity not in self._operational_device_pool:
                err_msg = f"The specified device '{device_identity}' is not available for checkout."
                raise CheckoutError(err_msg)

            del self._operational_device_pool[device_identity]
            self._operational_device_outstanding[device_identity] = device

        return

    def checkout_control_point(self, feature_name: str, **kwargs) -> ControlExtension:
        """
            Checkout control point (extension) from the operational pool.
        """

        extension = None
        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:

            control_key = None
            if feature_name == "power":
                if "server" in kwargs and "outlet" in kwargs:
                    # Format: power: outlet=0 server='someserver'
                    # We sort keys to ensure deterministic order, but based on user request example "outlet" came before "server" or after?
                    # User request: "power: server='someserver' outlet=0'"
                    # But also: "f"{feature}: paramk=paramv paramk=paramv"" implies sorted or specific order.
                    # I will use sorted keys to be consistent and deterministic.

                    param_parts = []
                    for k, v in sorted(kwargs.items()):
                        param_parts.append(f"{k}={repr(v)}")

                    control_key = f"{feature_name}: {' '.join(param_parts)}"

            if control_key is None:
                # Generic fallback for other features like serial
                if len(kwargs) > 0:
                    param_parts = []
                    for k, v in sorted(kwargs.items()):
                        param_parts.append(f"{k}={repr(v)}")

                    control_key = f"{feature_name}: {' '.join(param_parts)}"

            if control_key is None:
                err_msg = f"Could not determine control key for feature '{feature_name}' with parameters {kwargs}."
                raise CheckoutError(err_msg)

            if control_key not in self._operational_controlpoint_pool:
                err_msg = f"The specified control point '{control_key}' is not available for checkout."
                raise CheckoutError(err_msg)

            extension = self._operational_controlpoint_pool[control_key]

            del self._operational_controlpoint_pool[control_key]
            self._operational_controlpoint_outstanding[control_key] = extension

        return extension

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Establishes connectivity for all device coordinators.

            :param activation_params: Activation parameters used during initialization.
        """
        lscape = self.landscape

        layer_integ = lscape.layer_integration

        failures = []

        coordinators_for_services = layer_integ.coordinators_for_services
        for coord in coordinators_for_services.values():
            results = coord.establish_connectivity(activation_params)
            for item in results:
                host, ipaddr, status, stdout, stderr, exc = item
                if exc is not None:
                    failures.append(item)
                elif status is not None:
                    if isinstance(status, bool):
                        if not status:
                            failures.append(item)
                    elif status != 0:
                        failures.append(item)

        coordinators_for_power = layer_integ.coordinators_for_power
        for coord in coordinators_for_power.values():
            results = coord.establish_connectivity(activation_params)
            for item in results:
                host, ipaddr, status, stdout, stderr, exc = item
                if exc is not None:
                    failures.append(item)
                elif status is not None:
                    if isinstance(status, bool):
                        if not status:
                            failures.append(item)
                    elif status != 0:
                        failures.append(item)

        coordinators_for_serial = layer_integ.coordinators_for_serial
        for coord in coordinators_for_serial.values():
            results = coord.establish_connectivity(activation_params)
            for item in results:
                host, ipaddr, status, stdout, stderr, exc = item
                if exc is not None:
                    failures.append(item)
                elif status is not None:
                    if isinstance(status, bool):
                        if not status:
                            failures.append(item)
                    elif status != 0:
                        failures.append(item)

        coordinators_for_devices = layer_integ.coordinators_for_devices
        for coord in coordinators_for_devices.values():
            results = coord.establish_connectivity(activation_params)
            for item in results:
                host, ipaddr, status, stdout, stderr, exc = item
                if exc is not None:
                    failures.append(item)
                elif status is not None:
                    if isinstance(status, bool):
                        if not status:
                            failures.append(item)
                    elif status != 0:
                        failures.append(item)

        if len(failures) > 0:
            errmsg_lines = [
                "Errors encountered while establishing connectivity with the landscape.",
                "FAILURES:"
            ]

            for item in failures:
                host, ipaddr, status, stdout, stderr, exc = item
                if exc is not None:
                    errmsg_lines.append(f"    Host: {host} IP: {ipaddr} Exception: {exc}")
                else:
                    errmsg_lines.append(f"    Host: {host} IP: {ipaddr} Status: {status} Stderr: {stderr}")

            errmsg = os.linesep.join(errmsg_lines)

            # If we are not allowing missing devices, then raise a RuntimeError
            if not activation_params.allow_missing_devices:
                raise RuntimeError(errmsg)
            else:
                self.logger.error(errmsg)

        return
    
    def get_cluster_by_name(self, cluster_name: str) -> Union[LandscapeDeviceCluster, None]:
        """
            Retrieves a cluster by name from the operational layer.

            :param cluster_name: Name of the cluster to find.

            :returns: The matching cluster or ``None`` if not found.
            :rtype: Union[LandscapeDeviceCluster, None]
        """
        cluster = None

        lscape = self.landscape

        with lscape.begin_locked_landscape_scope() as locked:
            if cluster_name in self._operational_clusters:
                cluster = self._operational_clusters[cluster_name]
        
        return cluster

    def get_clusters(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None) -> List[LandscapeDeviceCluster]:
        """
            Gets a copy of the operational clusters list.
        """
        lscape = self.landscape

        candidate_clusters = None

        with lscape.begin_locked_landscape_scope() as locked:
            candidate_clusters = [dev for dev in self._operational_clusters.values()]
        
        selected_clusters = []

        if include_filters is None:
            selected_clusters = candidate_clusters
        else:
            while len(candidate_clusters):
                dev = candidate_clusters.pop()
                for ifilter in include_filters:
                    if ifilter.should_include(dev):
                        selected_clusters.append(dev)
                        break

        if exclude_filters is not None:
            candidate_clusters = selected_clusters

            selected_clusters = []

            while len(candidate_clusters):
                dev = candidate_clusters.pop()
                for xfilter in exclude_filters:
                    if not xfilter.should_exclude(dev):
                        selected_clusters.append(dev)

        return selected_clusters

    def overlay_toplogy(self, activation_params: LandscapeActivationParams):
        """
            Applies topology overlay information to the operational layer.

            :param activation_params: Activation parameters for the overlay.
        """
        lscape = self.landscape

        topology_info = lscape.layer_configuration.topology_info
        integ_layer = lscape.layer_integration

        if topology_info is not None:
            self._create_clusters(integ_layer, topology_info)

        self._operational_clusters_pool = self._operational_clusters.copy()

        return

    def validate_features(self, activation_params: LandscapeActivationParams):
        """
            Validates device feature availability if requested.

            :param activation_params: Activation parameters controlling validation.
        """
        if activation_params.validate_features:
            pass

        return
    
    def validate_topology(self, activation_params: LandscapeActivationParams):
        """
            Validates topology information if requested.

            :param activation_params: Activation parameters controlling validation.
        """
        if activation_params.validate_topology:
            pass

        return

    def _create_clusters(self, integ_layer: LandscapeIntegrationLayer, topology_info: Dict[str, Any]):
        """
            Creates operational clusters from topology configuration.

            :param integ_layer: Integration layer providing device groups.
            :param topology_info: Topology configuration dictionary.
        """
        table_of_device_groups = integ_layer.integrated_device_groups

        # ================= EXAMPLE ===================
        #
        #   - name: primary
        #     group: cluster/primary
        #     nodes:
        #         - mwalker-smbtest-green
        #         - mwalker-smbtest-orange
        #         - mwalker-smbtest-red
        #     spares:
        #         - mwalker-smbtest-yellow

        if "clusters" in topology_info:
            clusters = topology_info["clusters"]
            for cinfo in clusters:
                cname = cinfo["name"]
                group_name = cinfo["group"]

                nodes = []
                if "nodes" in cinfo:
                    nodes = cinfo["nodes"]
                
                spares = []
                if "spares" in cinfo:
                    spares = cinfo["spares"]

                if group_name in table_of_device_groups:
                    cgroup = table_of_device_groups[group_name]

                    coordinator: NodeCoordinatorBase = cgroup.coordinator
                    cluster = coordinator.create_cluster_for_devices(cname, cgroup, nodes, spares)

                    try:
                        cluster.enchance_metadata()
                    except Exception as xcpt:
                        errmsg_lines = [
                            "Error while attempting to enhance the metadata for a cluster.",
                            "EXCEPTION:"
                        ]

                        errmsg_lines.append(format_exception(xcpt))

                        errmsg = os.linesep.join(errmsg_lines)
                        raise RuntimeError(errmsg)

                    self._operational_clusters[cname] = cluster
        
        return

    def _initialize_operational_pools(self):
        """
            Initializes the operational pools from the integration layer.
        """
        lscape = self.landscape
        integ_layer = lscape.layer_integration

        self._operational_device_pool = integ_layer.integrated_devices.copy()

        self._operational_controlpoint_pool = {}

        coordinators_for_services = integ_layer.coordinators_for_services
        for svc_coord in coordinators_for_services.values():
            if hasattr(svc_coord, "creates_control_extensions") and svc_coord.creates_control_extensions:
                extensions = svc_coord.get_control_extensions()
                for key, ext in extensions:
                    self._operational_controlpoint_pool[key] = ext

        coordinators_for_power = integ_layer.coordinators_for_power
        for pwr_coord in coordinators_for_power.values():
            if hasattr(pwr_coord, "creates_control_extensions") and pwr_coord.creates_control_extensions:
                extensions = pwr_coord.get_control_extensions()
                for key, ext in extensions:
                    self._operational_controlpoint_pool[key] = ext

        coordinators_for_serial = integ_layer.coordinators_for_serial
        for serial_coord in coordinators_for_serial.values():
            if hasattr(serial_coord, "creates_control_extensions") and serial_coord.creates_control_extensions:
                extensions = serial_coord.get_control_extensions()
                for key, ext in extensions:
                    self._operational_controlpoint_pool[key] = ext

        return
