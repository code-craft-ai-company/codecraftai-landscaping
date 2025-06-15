"""
    .. module:: vspherecoordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the vspherecoordinatorcoupling functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.servicecoordinatorcouplingbase import ServiceCoordinatorCouplingBase

from automojo.landscaping.services.common import INTEGRATIION_CLASS_FOR_VSPHERE_VCENTER_SERVICE
from automojo.landscaping.services.vmware.vsphere.vspherecoordinator import VSphereCoordinator

class VSphereCoordinatorCoupling(ServiceCoordinatorCouplingBase):
    """
        Coupling object that registers the vSphere coordinator with the landscape.
    """

    integration_class: str = INTEGRATIION_CLASS_FOR_VSPHERE_VCENTER_SERVICE

    COORDINATOR_TYPE = VSphereCoordinator

    def __init__(self, *args, **kwargs):
        """
            Initializes the vSphere coordinator coupling.
        """
        super().__init__(*args, **kwargs)
        return
