"""
    .. module:: vsphereagent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the VSphereAgent object used to inter-operate with a VSphere server.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional

from  http import HTTPStatus

import requests

from automojo.credentials.basiccredential import BasicCredential

from automojo.landscaping.services.vmware.datastructures.specs.vmplacement import VmPlacementSpec

from automojo.landscaping.services.vmware.datastructures.vcenter import (
    DatacenterSummary, FolderSummary
)

from automojo.landscaping.services.vmware.vsphere.ext.certificatemanagementext import CertificateManagementExt
from automojo.landscaping.services.vmware.vsphere.ext.clusterext import ClusterExt
from automojo.landscaping.services.vmware.vsphere.ext.computeext import ComputeExt
from automojo.landscaping.services.vmware.vsphere.ext.contentext import ContentExt
from automojo.landscaping.services.vmware.vsphere.ext.cryptomanagerext import CryptoManagerExt
from automojo.landscaping.services.vmware.vsphere.ext.datacenterext import DataCenterExt
from automojo.landscaping.services.vmware.vsphere.ext.datastoreext import DataStoreExt
from automojo.landscaping.services.vmware.vsphere.ext.deploymentext import DeploymentExt
from automojo.landscaping.services.vmware.vsphere.ext.folderext import FolderExt
from automojo.landscaping.services.vmware.vsphere.ext.guestext import GuestExt
from automojo.landscaping.services.vmware.vsphere.ext.hostext import HostExt
from automojo.landscaping.services.vmware.vsphere.ext.hvcext import HvcExt
from automojo.landscaping.services.vmware.vsphere.ext.identityext import IdentityExt
from automojo.landscaping.services.vmware.vsphere.ext.inventoryext import InventoryExt
from automojo.landscaping.services.vmware.vsphere.ext.isoext import IsoExt
from automojo.landscaping.services.vmware.vsphere.ext.lcmext import LcmExt
from automojo.landscaping.services.vmware.vsphere.ext.namespacemanagementext import NamespaceManagementExt
from automojo.landscaping.services.vmware.vsphere.ext.namespacesext import NamespacesExt
from automojo.landscaping.services.vmware.vsphere.ext.networkext import NetworkExt
from automojo.landscaping.services.vmware.vsphere.ext.ovfext import OvfExt
from automojo.landscaping.services.vmware.vsphere.ext.resourcepoolext import ResourcePoolExt
from automojo.landscaping.services.vmware.vsphere.ext.servicesext import ServicesExt
from automojo.landscaping.services.vmware.vsphere.ext.storageext import StorageExt
from automojo.landscaping.services.vmware.vsphere.ext.systemconfigext import SystemConfigExt
from automojo.landscaping.services.vmware.vsphere.ext.taggingext import TaggingExt
from automojo.landscaping.services.vmware.vsphere.ext.tokenserviceext import TokenServiceExt
from automojo.landscaping.services.vmware.vsphere.ext.topologyext import TopologyExt
from automojo.landscaping.services.vmware.vsphere.ext.trustedinfrastructureext import TrustedInfrastructureExt
from automojo.landscaping.services.vmware.vsphere.ext.vmext import VmExt

class VSphereFilterState:
    """
        Maintains filter selections when interacting with vSphere.
    """

    def __init__(self) -> None:
        """
            Initializes a :class:`VSphereFilterState` instance.
        """
        self._working_datacenter = None
        self._working_folder = None
        return
    
    @property
    def working_datacenter(self) -> DatacenterSummary:
        """
            Returns the current working datacenter filter.

            :returns: Working datacenter summary.
            :rtype: DatacenterSummary
        """
        return self._working_datacenter

    @property
    def working_placement(self) -> VmPlacementSpec:
        """
            Creates a placement specification based on working filters.

            :returns: Placement specification populated from filters.
            :rtype: VmPlacementSpec
        """
        datastore = self._working_datacenter.datacenter
        folder = self._working_folder.folder
        placement = VmPlacementSpec(datastore=datastore, folder=folder)
        return placement

    @property
    def working_folder(self) -> FolderSummary:
        """
            Returns the current working folder filter.

            :returns: Folder summary instance.
            :rtype: FolderSummary
        """
        return self._working_folder

    def has_working_datacenter_filter(self):
        """
            Indicates if a working datacenter filter has been set.

            :returns: ``True`` if a datacenter filter exists.
            :rtype: bool
        """
        rtnval = self._working_datacenter is not None
        return rtnval
    
    def has_working_placement(self):
        """
            Indicates if both datacenter and folder filters have been set.

            :returns: ``True`` if a full placement is specified.
            :rtype: bool
        """
        rtnval = self._working_datacenter is not None and self._working_folder is not None
        return rtnval

    def has_working_folder_filter(self):
        """
            Indicates if a working folder filter has been set.

            :returns: ``True`` if a folder filter exists.
            :rtype: bool
        """
        rtnval = self._working_folder is not None
        return rtnval

    def set_working_datacenter(self, datacenter_summary: DatacenterSummary):
        """
            Sets the working datacenter filter.

            :param datacenter_summary: Datacenter summary to set.
        """
        self._working_datacenter = datacenter_summary
        return
    
    def set_working_folder(self, folder_summary: FolderSummary):
        """
            Sets the working folder filter.

            :param folder_summary: Folder summary to set.
        """
        self._working_folder = folder_summary
        return


class VSphereAgent:
    """
        Agent object used to issue requests to a vSphere server.
    """

    def __init__(self, host: str, credential: BasicCredential, verify_certificates: bool=False):
        """
            Creates a :class:`VSphereAgent` used to communicate with vSphere.

            :param host: Hostname or IP address of the vSphere server.
            :param credential: Credential used for authentication.
            :param verify_certificates: ``True`` to verify SSL certificates.
        """
        self._session = requests.session()
        self._session.verify = verify_certificates

        self._host = host
        self._credential = credential
        
        self._api_root = f"https://{host}/api"
        self._rest_root = f"https://{host}/rest" 

        self._auth_token = None

        self._ext_certificatemanagement = CertificateManagementExt(self)
        self._ext_cluster = ClusterExt(self)
        self._ext_compute = ComputeExt(self)
        self._ext_content = ContentExt(self)
        self._ext_cryptomanager = CryptoManagerExt(self)
        self._ext_datacenter = DataCenterExt(self)
        self._ext_datastore = DataStoreExt(self)
        self._ext_deployment = DeploymentExt(self)
        self._ext_folder = FolderExt(self)
        self._ext_guest = GuestExt(self)
        self._ext_host = HostExt(self)
        self._ext_hvc = HvcExt(self)
        self._ext_identity = IdentityExt(self)
        self._ext_inventory = InventoryExt(self)
        self._ext_iso = IsoExt(self)
        self._ext_lcm = LcmExt(self)
        self._ext_namespacemanagement = NamespaceManagementExt(self)
        self._ext_namespaces = NamespacesExt(self)
        self._ext_network = NetworkExt(self)
        self._ext_ovf = OvfExt(self)
        self._ext_resourcepool = ResourcePoolExt(self)
        self._ext_services = ServicesExt(self)
        self._ext_storage = StorageExt(self)
        self._ext_systemconfig = SystemConfigExt(self)
        self._ext_tagging = TaggingExt(self)
        self._ext_tokenservice = TokenServiceExt(self)
        self._ext_topology = TopologyExt(self)
        self._ext_trustedinfrastructure = TrustedInfrastructureExt(self)
        self._ext_vm = VmExt(self)

        self._filter_state = VSphereFilterState()

        return
    
    @property
    def filter_state(self) -> VSphereFilterState:
        """
            Returns the filter state used when building requests.

            :returns: Current :class:`VSphereFilterState` instance.
        """
        return self._filter_state

    @property
    def CertificateManagement(self) -> CertificateManagementExt:
        """
            Provides access to certificate management operations.

            :returns: Certificate management extension.
            :rtype: CertificateManagementExt
        """
        return self._ext_certificatemanagement
    
    @property
    def Cluster(self) -> ClusterExt:
        """
            Provides access to cluster operations.

            :returns: Cluster extension.
            :rtype: ClusterExt
        """
        return self._ext_cluster
    
    @property
    def Compute(self) -> ComputeExt:
        """
            Provides access to compute operations.

            :returns: Compute extension.
            :rtype: ComputeExt
        """
        return self._ext_compute
    
    @property
    def Content(self) -> ContentExt:
        """
            Provides access to content library operations.

            :returns: Content extension.
            :rtype: ContentExt
        """
        return self._ext_content

    @property
    def CryptoManager(self) -> CryptoManagerExt:
        """
            Provides access to cryptographic operations.

            :returns: Crypto manager extension.
            :rtype: CryptoManagerExt
        """
        return self._ext_cryptomanager

    @property
    def DataCenter(self) -> DataCenterExt:
        """
            Provides access to datacenter operations.

            :returns: Datacenter extension.
            :rtype: DataCenterExt
        """
        return self._ext_datacenter
    
    @property
    def DataStore(self) -> DataStoreExt:
        """
            Provides access to datastore operations.

            :returns: Datastore extension.
            :rtype: DataStoreExt
        """
        return self._ext_datastore
    
    @property
    def Deployment(self) -> DeploymentExt:
        """
            Provides access to deployment operations.

            :returns: Deployment extension.
            :rtype: DeploymentExt
        """
        return self._ext_deployment

    @property
    def Folder(self) -> FolderExt:
        """
            Provides access to folder operations.

            :returns: Folder extension.
            :rtype: FolderExt
        """
        return self._ext_folder

    @property
    def Guest(self) -> GuestExt:
        """
            Provides access to guest operations.

            :returns: Guest extension.
            :rtype: GuestExt
        """
        return self._ext_guest

    @property
    def Host(self) -> HostExt:
        """
            Provides access to host operations.

            :returns: Host extension.
            :rtype: HostExt
        """
        return self._ext_host
    
    @property
    def Hvc(self) -> HvcExt:
        """
            Provides access to hybrid vCenter operations.

            :returns: HVC extension.
            :rtype: HvcExt
        """
        return self._ext_hvc
    
    @property
    def Identity(self) -> IdentityExt:
        """
            Provides access to identity operations.

            :returns: Identity extension.
            :rtype: IdentityExt
        """
        return self._ext_identity
    
    @property
    def Inventory(self) -> InventoryExt:
        """
            Provides access to inventory operations.

            :returns: Inventory extension.
            :rtype: InventoryExt
        """
        return self._ext_inventory
    
    @property
    def Iso(self) -> IsoExt:
        """
            Provides access to ISO operations.

            :returns: ISO extension.
            :rtype: IsoExt
        """
        return self._ext_iso
    
    @property
    def Lcm(self) -> LcmExt:
        """
            Provides access to lifecycle management operations.

            :returns: LCM extension.
            :rtype: LcmExt
        """
        return self._ext_lcm
    
    @property
    def NamespaceManagement(self) -> NamespaceManagementExt:
        """
            Provides access to namespace management operations.

            :returns: Namespace management extension.
            :rtype: NamespaceManagementExt
        """
        return self._ext_namespacemanagement
    
    @property
    def Namespaces(self) -> NamespacesExt:
        """
            Provides access to namespace operations.

            :returns: Namespaces extension.
            :rtype: NamespacesExt
        """
        return self._ext_namespaces

    @property
    def Network(self) -> NetworkExt:
        """
            Provides access to network operations.

            :returns: Network extension.
            :rtype: NetworkExt
        """
        return self._ext_network
    
    @property
    def ResourcePool(self) -> ResourcePoolExt:
        """
            Provides access to resource pool operations.

            :returns: Resource pool extension.
            :rtype: ResourcePoolExt
        """
        return self._ext_resourcepool

    @property
    def Services(self) -> ServicesExt:
        """
            Provides access to service operations.

            :returns: Services extension.
            :rtype: ServicesExt
        """
        return self._ext_services
    
    @property
    def Storage(self) -> StorageExt:
        """
            Provides access to storage operations.

            :returns: Storage extension.
            :rtype: StorageExt
        """
        return self._ext_storage
    
    @property
    def SystemConfig(self) -> SystemConfigExt:
        """
            Provides access to system configuration operations.

            :returns: System configuration extension.
            :rtype: SystemConfigExt
        """
        return self._ext_systemconfig

    @property
    def Tagging(self) -> TaggingExt:
        """
            Provides access to tagging operations.

            :returns: Tagging extension.
            :rtype: TaggingExt
        """
        return self._ext_tagging
    
    @property
    def TokenService(self) -> TokenServiceExt:
        """
            Provides access to token service operations.

            :returns: Token service extension.
            :rtype: TokenServiceExt
        """
        return self._ext_tokenservice

    @property
    def Topology(self) -> TopologyExt:
        """
            Provides access to topology operations.

            :returns: Topology extension.
            :rtype: TopologyExt
        """
        return self._ext_topology
    
    @property
    def TrustedInfrastructure(self) -> TrustedInfrastructureExt:
        """
            Provides access to trusted infrastructure operations.

            :returns: Trusted infrastructure extension.
            :rtype: TrustedInfrastructureExt
        """
        return self._ext_trustedinfrastructure

    @property
    def Vm(self) -> VmExt:
        """
            Provides access to virtual machine operations.

            :returns: VM extension.
            :rtype: VmExt
        """
        return self._ext_vm

    def apply_working_folder_filter(self, container_path: str):
        """
            Applies a working folder filter using a container path.

            :param container_path: Datacenter and folder path in 'dc:/path' form.
        """
        dcrecord = None
        folderspec = None

        if container_path.find(":") >= 0:
            datacenter, folderspec = container_path.split(":")
            dcrecord = self.DataCenter.get_by_name(datacenter)
            self._filter_state.set_working_datacenter(dcrecord)

        folderspec = folderspec.lstrip("/")
        folder_leafs = folderspec.split("/")

        cont_folder = self.Folder.find_descendant(folder_leafs)
        self._filter_state.set_working_folder(cont_folder)

        return

    def build_api_url(self, leaf: str) -> str:
        """
            Builds a REST API URL for the given endpoint leaf.

            :param leaf: API leaf path to append.

            :returns: Full API URL string.
            :rtype: str
        """
        url = self._api_root + leaf
        
        return url

    def renew_session(self):
        """
            Renews the session authentication token using the stored credentials.
        """
        req_url = f"{self._rest_root}/com/vmware/cis/session"

        resp = self._session.post(req_url, auth=(self._credential.username, self._credential.password), verify=False)
        if resp.status_code == HTTPStatus.OK:
            rcontent = resp.json()
            self._auth_token = rcontent["value"]
            self._session.headers['vmware-api-session-id'] = self._auth_token
        else:
            resp.raise_for_status()
        
        return
    
    def session_delete(self, url: str, **kwargs) -> requests.Response:
        """
            Issues a DELETE request using the current session.

            :param url: Request URL.

            :returns: Response object from the request.
            :rtype: requests.Response
        """
        resp = self._session.delete(url, **kwargs)

        return resp

    def session_get(self, url: str, **kwargs) -> requests.Response:
        """
            Issues a GET request using the current session.

            :param url: Request URL.

            :returns: Response object from the request.
            :rtype: requests.Response
        """
        resp = self._session.get(url, **kwargs)

        return resp

    def session_post(self, url: str, data=None, json=None, **kwargs) -> requests.Response:
        """
            Issues a POST request using the current session.

            :param url: Request URL.
            :param data: Optional form data to send.
            :param json: Optional JSON body to send.

            :returns: Response object from the request.
            :rtype: requests.Response
        """
        resp = self._session.post(url, data=data, json=json, **kwargs)

        return resp
    
    def session_put(self, url: str, data=None, json=None, **kwargs) -> requests.Response:
        """
            Issues a PUT request using the current session.

            :param url: Request URL.
            :param data: Optional form data to send.
            :param json: Optional JSON body to send.

            :returns: Response object from the request.
            :rtype: requests.Response
        """
        resp = self._session.put(url, data=data, json=json, **kwargs)

        return resp

