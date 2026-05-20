# services/vmware Deprecations

Every module listed below is a one-release-cycle backwards-compatibility shim
that re-exports symbols from the new `automojo-interop-vsphere` package. All
shims emit a `DeprecationWarning` exactly once per process per import path on
first import.

All shims and the `_shim.py` helper are scheduled for deletion at the M13
milestone (one release after the M5 extraction landed).

## Removal schedule

Target removal release: **M13** (one cycle after M5 ships).

## Shim modules

### `vsphere/`

| Legacy import path                                                  | Replacement                                                  |
| ------------------------------------------------------------------- | ------------------------------------------------------------ |
| `automojo.landscaping.services.vmware.vsphere.vsphereagent`         | `automojo.interop.vsphere.vsphereclient.VSphereClient`        |
|                                                                     | `automojo.interop.vsphere.vspherefilterstate.VSphereFilterState` |

### `vsphere/ext/` (29 modules)

Every `*ext.py` re-exports the matching `*Group` from
`automojo.interop.vsphere.apigroups.*group`:

| Legacy module               | Legacy class                | New class                    |
| --------------------------- | --------------------------- | ---------------------------- |
| `baseext`                   | `BaseExt`                   | `BaseGroup`                  |
| `certificatemanagementext`  | `CertificateManagementExt`  | `CertificateManagementGroup` |
| `clusterext`                | `ClusterExt`                | `ClusterGroup`               |
| `computeext`                | `ComputeExt`                | `ComputeGroup`               |
| `contentext`                | `ContentExt`                | `ContentGroup`               |
| `cryptomanagerext`          | `CryptoManagerExt`          | `CryptoManagerGroup`         |
| `datacenterext`             | `DataCenterExt`             | `DatacenterGroup`            |
| `datastoreext`              | `DataStoreExt`              | `DatastoreGroup`             |
| `deploymentext`             | `DeploymentExt`             | `DeploymentGroup`            |
| `folderext`                 | `FolderExt`                 | `FolderGroup`                |
| `guestext`                  | `GuestExt`                  | `GuestGroup`                 |
| `hostext`                   | `HostExt`                   | `HostGroup`                  |
| `hvcext`                    | `HvcExt`                    | `HvcGroup`                   |
| `identityext`               | `IdentityExt`               | `IdentityGroup`              |
| `inventoryext`              | `InventoryExt`              | `InventoryGroup`             |
| `isoext`                    | `IsoExt`                    | `IsoGroup`                   |
| `lcmext`                    | `LcmExt`                    | `LcmGroup`                   |
| `namespacemanagementext`    | `NamespaceManagementExt`    | `NamespaceManagementGroup`   |
| `namespacesext`             | `NamespacesExt`             | `NamespacesGroup`            |
| `networkext`                | `NetworkExt`                | `NetworkGroup`               |
| `ovfext`                    | `OvfExt`                    | `OvfGroup`                   |
| `resourcepoolext`           | `ResourcePoolExt`           | `ResourcePoolGroup`          |
| `servicesext`               | `ServicesExt`               | `ServicesGroup`              |
| `storageext`                | `StorageExt`                | `StorageGroup`               |
| `systemconfigext`           | `SystemConfigExt`           | `SystemConfigGroup`          |
| `taggingext`                | `TaggingExt`                | `TaggingGroup`               |
| `tokenserviceext`           | `TokenServiceExt`           | `TokenServiceGroup`          |
| `topologyext`               | `TopologyExt`               | `TopologyGroup`              |
| `trustedinfrastructureext`  | `TrustedInfrastructureExt`  | `TrustedInfrastructureGroup` |
| `vmext`                     | `VmExt`                     | `VmGroup`                    |

### `datastructures/`

| Legacy module                                  | Symbols re-exported                                  | New home                                          |
| ---------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------- |
| `datastructures.vcenter`                       | `DatacenterSummary`, `FolderSummary`                 | `automojo.interop.vsphere.model.summary`          |
| `datastructures.model.summary`                 | `DatacenterSummary`, `FolderSummary`                 | `automojo.interop.vsphere.model.summary`          |
| `datastructures.model.vm`                      | `VirtualMachineSummary`, `VirtualMachineInfo`        | `automojo.interop.vsphere.model.vm`               |
| `datastructures.specs.vmcreate`                | `VmCreateSpec`                                       | `automojo.interop.vsphere.specs.vmcreate`         |
| `datastructures.specs.vmhardware`              | `VmHardwareSpec`                                     | `automojo.interop.vsphere.specs.vmhardware`       |
| `datastructures.specs.vmplacement`             | `VmPlacementSpec`                                    | `automojo.interop.vsphere.specs.vmplacement`      |
| `datastructures.specs.vmstorage`               | `VmStorageSpec`, `VmDiskSpec`, `VmStoragePolicySpec` (aliased to `VmStorageSpec`) | `automojo.interop.vsphere.specs.vmstorage`        |

### `metasphere/`

| Legacy module           | Legacy class         | New class          | New module                                     |
| ----------------------- | -------------------- | ------------------ | ---------------------------------------------- |
| `metasphere.vcenter`    | `VmPowerState`       | `PowerState`       | `automojo.interop.vsphere.enums.powerstate`    |
| `metasphere.vmguestos`  | `VmGuestOS`          | `GuestOs`          | `automojo.interop.vsphere.enums.guestos`       |
| `metasphere.vmhardware` | `VmHardwareVersion`  | `HardwareVersion`  | `automojo.interop.vsphere.enums.hardwareversion` |

## Symbols that did NOT survive the migration

The following legacy types were removed during the M5 extraction because they
were superseded by the new consolidated SchemaObjects or by plain string
fields. Callers that depended on them must migrate at the same time they move
off these shims:

- `metasphere.vcenter.FolderType` — replaced by plain string on
  `FolderSummary.type`.
- `metasphere.vmhardware` fine-grained backing/adapter/connection enums (e.g.
  `VmHardwareEthernetBackingType`, `VmHardwareAdapterScsiType`) — replaced by
  plain strings on `VmHardwareSpec`.
- `datastructures.model.summary.VmSummary` — replaced by
  `automojo.interop.vsphere.model.vm.VirtualMachineSummary`.
- `datastructures.model.vm.*` fine-grained dataclasses
  (`VmHardwareInfo`, `VmIdentityInfo`, `VmInfo`, etc.) — consolidated into
  `VirtualMachineInfo`.
- `datastructures.specs.vmhardware.*` fine-grained `*CreateSpec` / `*UpdateSpec`
  dataclasses — consolidated into `VmHardwareSpec`.
