"""
    .. module:: configurationextractor
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the configurationextractor functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import List, Optional

import copy

from ccai.interfaces.iexcludefilter import IExcludeFilter
from ccai.interfaces.iincludefilter import IIncludeFilter

from ccai.landscaping.wellknown import LandscapeSingleton

class ConfigurationExtractor:
    """
        The :class:`ConfigurationExtractor` is used to create an extraction from the Landscape,
        Topology, Runtime, Credentials.
    """

    def __init__(self):

        """
            Initializes the :class:`ConfigurationExtractor`.
        """

        self._landscape = LandscapeSingleton()
        
        self._description = {
            "apod": {
                "devices": []
            },
            "infrastructure": {
                "services": []
            }
        }

        return

    def extract_clusters(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None):
        """
            Extracts cluster device configurations from the landscape.

            :param include_filters: Optional include filters for selecting clusters.
            :param exclude_filters: Optional exclude filters for removing clusters.
        """

        devices_list = self._description["apod"]["devices"]

        clusters_found = self._landscape.get_clusters(include_filters=include_filters, exclude_filters=exclude_filters)

        for cluster in clusters_found:
            for node in cluster.nodes.values():
                devices_list.append(copy.deepcopy(node.device_config))

        return
    
    def extract_devices(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None):
        """
            Extracts device configurations from the landscape.

            :param include_filters: Optional include filters for selecting devices.
            :param exclude_filters: Optional exclude filters for removing devices.
        """

        devices_list = self._description["apod"]["devices"]

        devices_found = self._landscape.get_devices(include_filters=include_filters, exclude_filters=exclude_filters)

        for dev in devices_found:
            devices_list.append(copy.deepcopy(dev.device_config))

        return
    
    def extract_services(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None):
        """
            Extracts service configurations from the landscape.

            :param include_filters: Optional include filters for selecting services.
            :param exclude_filters: Optional exclude filters for removing services.
        """

        services_list = self._description["infrastructure"]["services"]

        services_found = self._landscape.get_services(include_filters=include_filters, exclude_filters=exclude_filters)

        for service in services_found:
            services_list.append(copy.deepcopy(service.service_config))

        return

    def get_configurations(self) -> dict:
        """
            Gets the configuration dictionary extracted from the runtime.

            :returns: Dictionary describing the extracted configuration.
        """
        return self._description
