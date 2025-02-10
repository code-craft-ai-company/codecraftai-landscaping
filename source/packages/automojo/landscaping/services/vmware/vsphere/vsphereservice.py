from typing import TYPE_CHECKING

from automojo.credentials.basecredential import BaseCredential
from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier
from automojo.landscaping.landscape import Landscape
from automojo.landscaping.services.servicebase import ServiceBase

from automojo.interop.services.vmware.vsphere.vsphereagent import VSphereAgent

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class VSphereService(ServiceBase):

    def __init__(self, lscape: Landscape, coordinator: CoordinatorBase, friendly_id: 
                 FriendlyIdentifier, service_type: str, service_config: dict):
        super().__init__(lscape, coordinator, friendly_id, service_type, service_config)
        
        credmgr = lscape.credential_manager

        self._credential_table = {}
        if "credentials" in service_config:
            for cred_name in service_config["credentials"]:
                self._credential_table[cred_name] = credmgr.lookup_credential(cred_name)
        
        self._credential = None
        for cred in self._credentials.values():
            if isinstance(cred, BaseCredential):
                self._credential = cred
                break
        
        self._vsagent = VSphereAgent(self.host, self._credential)
        return
    
    @property
    def vsagent(self):
        return self._vsagent
