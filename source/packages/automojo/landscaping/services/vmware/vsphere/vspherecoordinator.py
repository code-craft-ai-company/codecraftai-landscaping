"""
.. module:: vspherecoordinator
   :platform: Darwin, Linux, Unix, Windows
   :synopsis: Module containing the vspherecoordinator functionality.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional, TYPE_CHECKING
from automojo.landscaping.landscape import Landscape

from automojo.landscaping.services.servicecoordinatorbase import ServiceCoordinatorBase

from automojo.landscaping.services.common import INTEGRATIION_CLASS_FOR_VSPHERE_VCENTER_SERVICE
from automojo.landscaping.services.vmware.vsphere.vsphereservice import VSphereService

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape

class VSphereCoordinator(ServiceCoordinatorBase):
    """
    """

    INTEGRATION_CLASS = INTEGRATIION_CLASS_FOR_VSPHERE_VCENTER_SERVICE
    SERVICE_TYPE = VSphereService

    # pylint: disable=attribute-defined-outside-init

    def __init__(self, lscape: Landscape, *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)
        return
