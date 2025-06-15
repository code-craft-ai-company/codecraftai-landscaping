"""
    .. module:: vm
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the vm functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional

from dataclasses import dataclass

from automojo.landscaping.services.vmware.metasphere.vmguestos import VmGuestOS
from automojo.landscaping.services.vmware.metasphere.vmhardware import (
    VmHardwareConnectionState,
    VmHardwareSerialBackingType,
    VmHardwareBootDeviceType,
    VmHardwareCdromDeviceAccessType,
    VmHardwareCdromBackingType,
    VmHardwareCdromHostBusAdapterType,
    VmHardwareDiskBackingType,
    VmHardwareDiskHostBusAdapterType,
    VmHardwareFloppyBackingType,
    VmHardwareUpgradePolicy,
    VmHardwareUpgradeStatus,
    VmHardwareVersion,
    VmHardwareAdapterScsiSharing,
    VmHardwareAdapterScsiType,
    VmHardwareBootType,
    VmHardwareBootNetworkProtocol,
    VmHardwareEthernetBackingType,
    VmHardwareEthernetMacAddressType,
    VmHardwareEthernetEmulationType,
    VmHardwareAdapterSataType,
    VmHardwareParallelBackingType,
    VmPowerState
)

@dataclass
class VmHardwareSerialBackingInfo:
    """
        Backing information for a virtual serial port.
    """
    type: VmHardwareSerialBackingType
    auto_detect: Optional[bool] = None
    file: Optional[str] = None
    host_device: Optional[str] = None
    network_location: Optional[str] = None
    no_rx_loss: Optional[str] = None
    pipe: Optional[str] = None
    proxy: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareSerialBackingInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareSerialBackingInfo`.
        """
        obj = VmHardwareSerialBackingInfo(**info)
        return obj
    

@dataclass
class VmHardwareSerialInfo:
    """
        Information for a virtual serial port device.
    """
    allow_guest_control: bool
    backing: VmHardwareSerialBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState
    yield_on_poll: bool

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareSerialInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareSerialInfo`.
        """
        info["backing"] = VmHardwareSerialBackingInfo.from_dict(info["backing"])
        obj = VmHardwareSerialInfo(**info)
        return obj

@dataclass
class VmHardwareBootDeviceEntry:
    """
        Entry describing a bootable device on a virtual machine.
    """
    type: VmHardwareBootDeviceType
    disks: List[str]
    nic: str

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareBootDeviceEntry":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareBootDeviceEntry`.
        """
        obj = VmHardwareBootDeviceEntry(**info)
        return obj

@dataclass
class VmHardwareCdromBackingInfo:
    """
        Backing information for a virtual CD-ROM device.
    """
    iso_file: str
    type: VmHardwareCdromBackingType
    auto_detect: Optional[bool] = None
    device_access_type: Optional[VmHardwareCdromDeviceAccessType] = None
    host_device: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCdromBackingInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareCdromBackingInfo`.
        """
        obj = VmHardwareCdromBackingInfo(**info)
        return obj

@dataclass
class VmHardwareIdeAddressInfo:
    """
        IDE address information for a virtual device.
    """
    master: bool
    primary: bool

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareIdeAddressInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareIdeAddressInfo`.
        """
        obj = VmHardwareIdeAddressInfo(**info)
        return obj

@dataclass
class VmHardwareNvmeAddressInfo:
    """
        NVMe address information for a virtual device.
    """
    bus: int
    unit: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareNvmeAddressInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareNvmeAddressInfo`.
        """
        obj = VmHardwareNvmeAddressInfo(**info)
        return obj


@dataclass
class VmHardwareSataAddressInfo:
    """
        SATA address information for a virtual device.
    """
    bus: int
    unit: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareSataAddressInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareSataAddressInfo`.
        """
        obj = VmHardwareSataAddressInfo(**info)
        return obj

@dataclass
class VmHardwareScsiAddressInfo:
    """
        SCSI address information for a virtual device.
    """
    bus: int
    unit: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareScsiAddressInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareScsiAddressInfo`.
        """
        obj = VmHardwareScsiAddressInfo(**info)
        return obj

@dataclass
class VmHardwareCdromInfo:
    """
        Information describing a CD-ROM device.
    """
    allow_guest_control: bool
    backing: VmHardwareCdromBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState
    type: VmHardwareCdromHostBusAdapterType
    ide: Optional[VmHardwareIdeAddressInfo] = None
    sata: Optional[VmHardwareSataAddressInfo] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCdromInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareCdromInfo`.
        """
        info["backing"] = VmHardwareCdromBackingInfo.from_dict(info["backing"])
        if "ide" in info:
            info["ide"] = VmHardwareIdeAddressInfo.from_dict(info["ide"])
        if "sata" in info:
            info["sata"] = VmHardwareSataAddressInfo.from_dict(info["sata"])
        obj = VmHardwareCdromInfo(**info)
        return obj

@dataclass
class VmHardwareCpuInfo:
    """
        Information describing the CPU configuration of a VM.
    """
    cores_per_socket: int
    count: int
    hot_add_enabled: bool
    hot_remove_enabled: bool

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCpuInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareCpuInfo`.
        """
        obj = VmHardwareCpuInfo(**info)
        return obj

@dataclass
class VmHardwareDiskBackingInfo:
    """
        Backing information for a virtual disk device.
    """
    type: VmHardwareDiskBackingType
    vmdk_file: str

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareDiskBackingInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareDiskBackingInfo`.
        """
        obj = VmHardwareDiskBackingInfo(**info)
        return obj

@dataclass
class VmHardwareDiskInfo:
    """
        Information describing a virtual disk device.
    """
    backing: VmHardwareDiskBackingInfo
    type: VmHardwareDiskHostBusAdapterType
    label: str
    ide: Optional[VmHardwareIdeAddressInfo] = None
    nvme: Optional[VmHardwareNvmeAddressInfo] = None
    sata: Optional[VmHardwareSataAddressInfo] = None
    scsi: Optional[VmHardwareScsiAddressInfo] = None
    capacity: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareCdromInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareCdromInfo`.
        """
        info["backing"] = VmHardwareDiskBackingInfo.from_dict(info["backing"])
        if "ide" in info:
            info["ide"] = VmHardwareIdeAddressInfo.from_dict(info["ide"])
        if "nvme" in info:
            info["nvme"] = VmHardwareNvmeAddressInfo.from_dict(info["nvme"])
        if "sata" in info:
            info["sata"] = VmHardwareSataAddressInfo.from_dict(info["sata"])
        if "scsi" in info:
            info["scsi"] = VmHardwareScsiAddressInfo.from_dict(info["scsi"])
        obj = VmHardwareDiskInfo(**info)
        return obj

@dataclass
class VmHardwareFloppyBackingInfo:
    """
        Backing information for a virtual floppy device.
    """
    type: VmHardwareFloppyBackingType
    auto_detect: Optional[bool] = None
    host_device: Optional[str] = None
    image_file: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareFloppyBackingInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareFloppyBackingInfo`.
        """
        obj = VmHardwareFloppyBackingInfo(**info)
        return obj

@dataclass
class VmHardwareFloppyInfo:
    """
        Information describing a virtual floppy device.
    """
    allow_guest_control: bool
    backing: VmHardwareFloppyBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareFloppyInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareFloppyInfo`.
        """
        info["backing"] = VmHardwareFloppyBackingInfo.from_dict(info["backing"])
        obj = VmHardwareFloppyInfo(**info)
        return obj


@dataclass
class VmHardwareInfo:
    """
        Overall hardware information for a virtual machine.
    """
    upgrade_policy: VmHardwareUpgradePolicy
    upgrade_status: VmHardwareUpgradeStatus
    version: VmHardwareVersion
    upgrade_error: Optional[dict] = None
    upgrade_version: Optional[VmHardwareVersion] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareInfo`.
        """
        obj = VmHardwareInfo(**info)
        return obj

@dataclass
class VmHardwareAdapterScsiInfo:
    """
        Information describing a SCSI adapter in a VM.
    """
    label: str
    scsi: VmHardwareScsiAddressInfo
    sharing: VmHardwareAdapterScsiSharing
    type: VmHardwareAdapterScsiType
    pci_slot_number: int

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterScsiInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareAdapterScsiInfo`.
        """
        info["scsi"] = VmHardwareScsiAddressInfo.from_dict(info["scsi"])
        obj = VmHardwareAdapterScsiInfo(**info)
        return obj

@dataclass
class VmHardwareBootInfo:
    """
        Boot configuration information for a VM.
    """
    delay: int
    enter_setup_mode: bool
    retry: bool
    retry_delay: int
    type: VmHardwareBootType
    network_protocol: Optional[VmHardwareBootNetworkProtocol] = None
    efi_legacy_boot: Optional[bool] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareBootInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareBootInfo`.
        """
        obj = VmHardwareBootInfo(**info)
        return obj

@dataclass
class VmHardwareMemoryInfo:
    """
        Information describing the memory configuration of a VM.
    """
    hot_add_enabled: bool
    size_MiB: int
    hot_add_increment_size_MiB: Optional[int] = None
    hot_add_limit_MiB: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareMemoryInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareMemoryInfo`.
        """
        obj = VmHardwareMemoryInfo(**info)
        return obj


@dataclass
class VmHardwareEthernetBackingInfo:
    """
        Backing information for a virtual ethernet device.
    """
    type: VmHardwareEthernetBackingType
    connection_cookie: Optional[int] = None
    distributed_port: Optional[str] = None
    distributed_switch_uuid: Optional[str] = None
    host_device: Optional[str] = None
    network: Optional[str] = None
    network_name: Optional[str] = None
    opaque_network_id: Optional[str] = None
    opaque_network_type: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareEthernetBackingInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareEthernetBackingInfo`.
        """
        obj = VmHardwareEthernetBackingInfo(**info)
        return obj

@dataclass
class VmHardwareEthernetInfo:
    """
        Information describing a virtual ethernet device.
    """
    allow_guest_control: bool
    backing: VmHardwareEthernetBackingInfo
    label: str
    mac_type: VmHardwareEthernetMacAddressType
    start_connected: bool
    state: VmHardwareConnectionState
    type: VmHardwareEthernetEmulationType
    wake_on_lan_enabled: bool
    mac_address: Optional[str] = None
    pci_slot_number: Optional[int] = None
    upt_compatibility_enabled: Optional[bool] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareEthernetInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareEthernetInfo`.
        """
        info["backing"] = VmHardwareEthernetBackingInfo.from_dict(info["backing"])
        obj = VmHardwareEthernetInfo(**info)
        return obj

@dataclass
class VmHardwareAdapterSataInfo:
    """
        Information describing a SATA adapter in a VM.
    """
    bus: int
    label: str
    type: VmHardwareAdapterSataType
    pci_slot_number: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterSataInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareAdapterSataInfo`.
        """
        obj = VmHardwareAdapterSataInfo(**info)
        return obj

@dataclass
class VmHardwareParallelBackingInfo:
    """
        Backing information for a virtual parallel port.
    """
    type: VmHardwareParallelBackingType
    auto_detect: Optional[bool] = None
    file: Optional[str] = None
    host_device: Optional[str] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareParallelBackingInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareParallelBackingInfo`.
        """
        obj = VmHardwareParallelBackingInfo(**info)
        return obj

@dataclass
class VmHardwareParallelInfo:
    """
        Information describing a virtual parallel port.
    """
    allow_guest_control: bool
    backing: VmHardwareParallelBackingInfo
    label: str
    start_connected: bool
    state: VmHardwareConnectionState

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareParallelInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareParallelInfo`.
        """
        info["backing"] = VmHardwareParallelBackingInfo.from_dict(info["backing"])
        obj = VmHardwareParallelInfo(**info)
        return obj

@dataclass
class VmHardwareAdapterNvmeInfo:
    """
        Information describing an NVMe adapter in a VM.
    """
    bus: int
    label: str
    pci_slot_number: Optional[int] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterNvmeInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareAdapterNvmeInfo`.
        """
        obj = VmHardwareAdapterNvmeInfo(**info)
        return obj

@dataclass
class VmIdentityInfo:
    """
        Identification information for a virtual machine.
    """
    bios_uuid: str
    instance_uuid: str
    name: str

    @classmethod
    def from_dict(cls, info: dict) -> "VmIdentityInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmIdentityInfo`.
        """
        obj = VmIdentityInfo(**info)
        return obj

@dataclass
class VmInfo:
    """
        Comprehensive information describing a virtual machine.
    """
    serial_ports: List[VmHardwareSerialInfo]
    boot_devices: List[VmHardwareBootDeviceEntry]
    cdroms: List[VmHardwareCdromInfo]
    cpu: VmHardwareCpuInfo
    disks: List[VmHardwareDiskInfo]
    floppies: List[VmHardwareFloppyInfo]
    guest_OS: VmGuestOS
    hardware: VmHardwareInfo
    scsi_adapters: List[VmHardwareAdapterScsiInfo]
    boot: VmHardwareBootInfo
    memory: VmHardwareMemoryInfo
    name: str
    nics: List[VmHardwareEthernetInfo]
    sata_adapters: List[VmHardwareAdapterSataInfo]
    parallel_ports: List[VmHardwareParallelInfo]
    power_state: VmPowerState
    nvme_adapters: Optional[List[VmHardwareAdapterNvmeInfo]] = None
    identity: Optional[VmIdentityInfo] = None
    instant_clone_frozen: Optional[bool] = None

    @classmethod
    def from_dict(cls, info: dict) -> "VmHardwareAdapterNvmeInfo":
        """
            Creates an instance from a dictionary of attributes.

            :param info: Dictionary representing the object.

            :returns: Instantiated :class:`VmHardwareAdapterNvmeInfo`.
        """

        info["serial_ports"] = [VmHardwareSerialInfo.from_dict(item) for item in info["serial_ports"]]
        info["boot_devices"] = [VmHardwareBootDeviceEntry.from_dict(item) for item in info["boot_devices"]]
        info["cdroms"] = { key: VmHardwareCdromInfo.from_dict(item) for key, item in info["cdroms"].items() }
        info["cpu"] = VmHardwareCpuInfo.from_dict(info["cpu"])
        info["disks"] = { key: VmHardwareDiskInfo.from_dict(item) for key, item in info["disks"].items() }
        info["floppies"] = { key: VmHardwareFloppyInfo.from_dict(item) for key, item in info["floppies"].items() }
        info["hardware"] = VmHardwareInfo.from_dict(info["hardware"])
        info["scsi_adapters"] = { key: VmHardwareAdapterScsiInfo.from_dict(item) for key, item in info["scsi_adapters"].items() }
        info["boot"] = VmHardwareBootInfo.from_dict(info["boot"])
        info["memory"] = VmHardwareMemoryInfo.from_dict(info["memory"])
        info["nics"] = { key: VmHardwareEthernetInfo.from_dict(item) for key, item in info["nics"].items() }
        info["sata_adapters"] = { key: VmHardwareAdapterSataInfo.from_dict(item) for key, item in info["sata_adapters"].items() }
        info["parallel_ports"] = { key: VmHardwareParallelInfo.from_dict(item) for key, item in info["parallel_ports"].items() }
        if "nvme_adapters" in info:
            info["nvme_adapters"] = { key: VmHardwareAdapterNvmeInfo.from_dict(item) for key, item in info["nvme_adapters"].items() }
        if "identity" in info:
            info["identity"] = VmIdentityInfo.from_dict(info["identity"])

        obj = VmHardwareAdapterNvmeInfo(**info)
        return obj
