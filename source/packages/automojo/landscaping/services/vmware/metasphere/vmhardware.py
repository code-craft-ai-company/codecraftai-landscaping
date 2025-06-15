"""
    .. module:: vmhardware
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains various VM hardware related enumerations.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

class VmHardwareVersion:
    """
        Defines VMware virtual hardware versions.
    """
    VMX_03 = "VMX_03"
    VMX_04 = "VMX_04"
    VMX_06 = "VMX_06"
    VMX_07 = "VMX_07"
    VMX_08 = "VMX_08"
    VMX_09 = "VMX_09"
    VMX_10 = "VMX_10"
    VMX_11 = "VMX_11"
    VMX_12 = "VMX_12"
    VMX_13 = "VMX_13"
    VMX_14 = "VMX_14"
    VMX_15 = "VMX_15"
    VMX_16 = "VMX_16"
    VMX_17 = "VMX_17"
    VMX_18 = "VMX_18"
    VMX_19 = "VMX_19"
    VMX_20 = "VMX_20"

class VmHardwareBootNetworkProtocol:
    """
        Enumeration of boot network protocols for VMs.
    """
    IPV4 = "IPV4"
    IPV6 = "IPV6"

class VmHardwareBootType:
    """
        Enumeration of boot types for virtual machines.
    """
    BIOS = "BIOS"
    EFI = "EFI"

class VmHardwareDiskBackingType:
    """
        Types of disk backing available for virtual disks.
    """
    VMDK_FILE = "VMDK_FILE"

class VmHardwareDiskHostBusAdapterType:
    """
        Host bus adapter types for virtual disks.
    """
    IDE = "IDE"
    SCSI = "SCSI"
    SATA = "SATA"
    NVME = "NVME"

class VmHardwareFloppyBackingType:
    """
        Backing types for floppy devices.
    """
    IMAGE_FILE = "IMAGE_FILE"
    HOST_DEVICE = "HOST_DEVICE"
    CLIENT_DEVICE = "CLIENT_DEVICE"

class VmHardwareCdromDeviceAccessType:
    """
        Access modes for virtual CD-ROM devices.
    """
    EMULATION = "EMULATION"
    PASSTHRU = "PASSTHRU"
    PASSTHRU_EXCLUSIVE = "PASSTHRU_EXCLUSIVE"

class VmHardwareCdromBackingType:
    """
        Backing types for virtual CD-ROM devices.
    """
    ISO_FILE = "ISO_FILE"
    HOST_DEVICE = "HOST_DEVICE"
    CLIENT_DEVICE = "CLIENT_DEVICE"

class VmHardwareCdromHostBusAdapterType:
    """
        Host bus adapter types for CD-ROM devices.
    """
    IDE = "IDE"
    SATA = "SATA"

class VmHardwareEthernetBackingType:
    """
        Backing types for virtual Ethernet adapters.
    """
    STANDARD_PORTGROUP = "STANDARD_PORTGROUP"
    HOST_DEVICE = "HOST_DEVICE"
    DISTRIBUTED_PORTGROUP = "DISTRIBUTED_PORTGROUP"
    OPAQUE_NETWORK = "OPAQUE_NETWORK"

class VmHardwareEthernetMacAddressType:
    """
        MAC address assignment types for virtual Ethernet adapters.
    """
    MANUAL = "MANUAL"
    GENERATED = "GENERATED"
    ASSIGNED = "ASSINGED"

class VmHardwareEthernetEmulationType:
    """
        Emulation types for virtual Ethernet adapters.
    """
    E1000 = "E1000"
    E1000E = "E1000E"
    PCNET32 = "PCNET32"
    VMXNET = "VMXNET"
    VMXNET2 = "VMXNET2"
    VMXNET3 = "VMXNET3"

class VmHardwareParallelBackingType:
    """
        Backing types for parallel ports.
    """
    FILE = "FILE"
    HOST_DEVICE = "HOST_DEVICE"

class VmHardwareBootDeviceType:
    """
        Boot devices that can be configured for VMs.
    """
    CDROM = "CDROM"
    DISK = "DISK"
    ETHERNET = "ETHERNET"
    FLOPPY = "FLOPPY"

class VmHardwareAdapterSataType:
    """
        SATA adapter types for virtual machines.
    """
    AHCI = "AHCI"

class VmHardwareAdapterScsiSharing:
    """
        SCSI adapter sharing modes.
    """
    NONE = "NONE"
    VIRTUAL = "VIRTUAL"
    PHYSICAL = "PHYSICAL"

class VmHardwareAdapterScsiType:
    """
        SCSI adapter types for virtual machines.
    """
    BUSLOGIC = "BUSLOGIC"
    LSILOGIC = "LSILOGIC"
    LSILOGICSAS = "LSILOGICSAS"
    PVSCSI = "PVSCSI"

class VmHardwareSerialBackingType:
    """
        Backing types for serial ports.
    """
    FILE = "FILE"
    HOST_DEVICE = "HOST_DEVICE"
    PIPE_SERVER = "PIPE_SERVER"
    PIPE_CLIENT = "PIPE_CLIENT"
    NETWORK_SERVER = "NETWORK_SERVER"
    NETWORK_CLIENT = "NETWORK_CLIENT"

class VmHardwareConnectionState:
    """
        Connection states for virtual hardware components.
    """
    CONNECTED = "CONNECTED"
    RECOVERABLE_ERROR = "RECOVERABLE_ERROR"
    UNRECOVERABLE_ERROR = "UNRECOVERABLE_ERROR"
    NOT_CONNECTED = "NOT_CONNECTED"
    UNKNOWN = "UNKNOWN"

class VmHardwareUpgradePolicy:
    """
        Policies controlling virtual hardware upgrades.
    """
    NEVER = "NEVER"
    AFTER_CLEAN_SHUTDOWN = "AFTER_CLEAN_SHUTDOWN"
    ALWAYS = "ALWAYS"

class VmHardwareUpgradeStatus:
    """
        Possible results of hardware upgrade operations.
    """
    NONE = "NONE"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class VmHardwareAdapterScsiSharing:
    """
        SCSI adapter sharing settings for controllers.
    """
    NONE = "NONE"
    VIRTUAL = "VIRTUAL"
    PHYSICAL = "PHYSICAL"

class VmPowerState:
    """
        States that a virtual machine may be in.
    """
    POWERED_OFF = "POWERED_OFF"
    POWERED_ON = "POWERED_ON"
    SUSPENDED = "SUSPENDED"