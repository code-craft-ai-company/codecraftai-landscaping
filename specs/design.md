# AutoMojo Landscaping Package Design Document

## Overview

The AutoMojo Landscaping package is a comprehensive test automation framework designed to manage and orchestrate test environments containing diverse devices, services, and infrastructure components. It provides a sophisticated layered architecture for configuration, integration, and operational management of automation resources across multiple platforms (Linux, macOS, Windows). The framework supports complex scenarios including device clustering, protocol extensions, resource pooling, and orchestration jobs while maintaining thread safety and extensibility.

## Architecture

### Core Design Principles

1. **Layered Architecture**: The system uses a multi-layer approach separating concerns:
   - Configuration Layer: Handles loading and validation of landscape configurations
   - Integration Layer: Manages device and service discovery and integration
   - Operational Layer: Provides runtime management and coordination

2. **Singleton Pattern**: The `Landscape` class serves as a central singleton providing global access to automation resources

3. **Coordinator Pattern**: Device and service management is delegated to specialized coordinators responsible for specific device types or protocols

4. **Extension System**: Devices and services can be enhanced with protocol-specific extensions (SSH, UPNP, REST, etc.)

5. **Thread Safety**: All core components implement proper locking mechanisms for concurrent access

### Core Components

#### Landscape (Central Orchestrator)
- **File**: `landscape.py`
- **Purpose**: Central singleton managing the entire test environment lifecycle
- **Key Features**:
  - Three-phase activation: Configuration → Integration → Operations
  - Thread-safe singleton implementation with initialization gates
  - Layered functionality through MixIn pattern
  - Device/service checkout/checkin for resource management
  - Credential management integration
  - Interactive and non-interactive mode support

#### Five-Layer Architecture

##### Installation Layer (`LandscapeInstallationLayer`)
- **Purpose**: Manages integration coupling installation and discovery
- **Responsibilities**:
  - Loading integration coupling types from configured factories
  - Managing installed integration couplings registry
  - Providing coupling type lookup and registration

##### Configuration Layer (`LandscapeConfigurationLayer`)
- **Purpose**: Loads and validates landscape and topology configurations
- **Responsibilities**:
  - Configuration file loading and merging (landscape, topology, credentials)
  - Multi-level validation with error and warning reporting
  - Credential manager initialization
  - Environment attachment for integration couplings
  - Configuration recording for debugging

##### Integration Layer (`LandscapeIntegrationLayer`)
- **Purpose**: Discovers and integrates devices and services into the landscape
- **Responsibilities**:
  - Device and service initialization from configuration
  - Coordinator creation and management
  - Integration coupling registration and dependency management
  - Device grouping and organization
  - Protocol extension registration

##### Operational Layer (`LandscapeOperationalLayer`)
- **Purpose**: Provides runtime management and coordination
- **Responsibilities**:
  - Coordinator activation and connectivity establishment
  - Topology overlay and cluster creation
  - Feature and topology validation
  - Resource pool management (checkout/checkin for devices and clusters)
  - Device and cluster availability tracking

##### Topology Integration Layer (`TopologyIntegrationLayer`)
- **Purpose**: Handles topology-specific integration concerns
- **Responsibilities**:
  - Topology configuration processing
  - Network and cluster relationship management

#### Device Management

##### LandscapeDevice
- **Purpose**: Base class for all automation devices in the landscape
- **Key Features**:
  - Thread-safe device operations with locking scopes
  - Protocol extension attachment system
  - Credential management per device
  - Feature-based filtering and matching
  - Status verification callbacks
  - IP address resolution and caching
  - Contact timestamp tracking (first/last contact)
  - Device isolation and watching capabilities

##### Device Coordinators (`CoordinatorBase`)
- **Purpose**: Manage specific types of devices or protocols
- **Responsibilities**:
  - Device discovery and creation
  - Connectivity establishment and verification
  - Device enhancement and configuration
  - Protocol-specific operations
  - Thread-safe device pool management
  - Expected vs found device tracking

##### Client Implementations
- **Platform-Specific Clients**: Linux, macOS, Windows client implementations
- **Base Class**: `ClientBase` providing common client functionality
- **Client Coordinators**: `ClientCoordinatorBase` with SSH integration support
- **Extensions**: Platform-specific extensions for commands, configuration, etc.

##### Specialized Device Types
- **NodeBase**: Base class for cluster node devices
- **SshDevice**: SSH-specific device implementation
- **Client Types**: LinuxClient, OSXClient, WindowsClient with platform extensions

#### Service Management

##### LandscapeService
- **Purpose**: Represents services available in the test landscape
- **Features**: Similar to devices but focused on service-specific operations
- **Key Capabilities**:
  - Service-specific credential management
  - Protocol extension support
  - Service grouping and organization
  - Thread-safe service operations
  - Status verification and monitoring

##### Service Coordinators
- **ServiceCoordinatorBase**: Base class for service management
- **ServiceBase**: Base implementation for common service functionality
- **Integration**: Managed through service coordinators with coupling support

#### Integration System

##### Coupling Architecture
- **CoordinatorCoupling**: Base class for integrating coordinators into the landscape
- **IntegrationCoupling**: Provides integration points for external systems
- **Factory Pattern**: Automated registration and creation of couplings
- **Integration Keys**: Structured keys for coupling identification (e.g., "apod:devices:deviceType:network/ssh")

##### Extension System
- **ProtocolExtension**: Base for protocol-specific device enhancements
- **DeviceExtensionType**: Enumeration of supported extension types (SSH, UPNP, REST)
- **Dynamic Attachment**: Extensions can be attached to devices at runtime
- **Extension Initialization**: Weak reference management for coordinator and device relationships

#### Device Clustering and Grouping

##### Device Clusters (`LandscapeDeviceCluster`)
- **Purpose**: Manages groups of devices that form compute clusters
- **Features**:
  - Active node and spare node management
  - Cluster-level checkout/checkin operations
  - Metadata enhancement capabilities
  - Integration with device groups

##### Device Groups (`LandscapeDeviceGroup`)
- **Purpose**: Organizes devices by group labels
- **Features**:
  - Automatic grouping based on device configuration
  - Coordinator reference management
  - Group-based device operations

##### Node Management
- **NodeBase**: Base class for cluster nodes
- **NodeCoordinatorBase**: Specialized coordinators for cluster management
- **Cluster Creation**: Dynamic cluster creation from topology configuration

### Configuration Management

#### Configuration Structure
- **Landscape Configuration**: Defines devices, services, and environment settings
- **Topology Configuration**: Describes relationships, networks, and cluster topology
- **Credential Configuration**: Manages authentication credentials
- **Runtime Configuration**: Dynamic runtime parameters

#### Configuration Validation
- Multi-level validation with error and warning reporting
- Integration coupling validation
- Device and service configuration validation
- Topology validation with cluster and network validation

#### Configuration Extraction
- **ConfigurationExtractor**: Exports filtered configurations
- **Selective Extraction**: Support for device, service, and cluster filtering
- **Format Preservation**: Maintains original configuration structure

#### Activation Parameters
- **LandscapeActivationParams**: Controls activation behavior
- **Configurable Options**:
  - Device/service activation enable/disable
  - Missing device/service tolerance
  - Feature and topology validation control

### Threading and Concurrency

#### Locking Strategy
- **Landscape Lock**: Global RLock for landscape-wide operations
- **Device Locks**: Individual RLocks for each device
- **Service Locks**: Individual RLocks for each service
- **Coordinator Locks**: Individual RLocks for each coordinator

#### Scope Management
- **LockedScope**: Context manager for acquiring locks
- **UnLockedScope**: Context manager for temporarily releasing locks
- **Nested Locking**: Support for nested lock acquisition

### Platform Support

#### Multi-Platform Architecture
- **Linux**: Full support with LinuxClient and extensions (commands, configuration)
- **macOS**: OSX client implementation with platform-specific coordinators
- **Windows**: Windows client implementation with platform-specific coordinators
- **Extensible**: Plugin architecture for additional platforms
- **Specialized Platforms**: Raspberry Pi cluster support

#### Protocol Support
- **SSH**: Secure Shell protocol for remote command execution
- **Serial**: Serial communication for embedded devices (TCP serial support)
- **Power**: Power management and control (DLI Power support)
- **UPNP**: Universal Plug and Play discovery
- **REST**: RESTful API interactions
- **VMware**: VMware vSphere and Workstation integration

#### Coordinator Specializations
- **SSH Coordinator**: Direct SSH device management
- **Power Coordinators**: Device power control management
- **Serial Coordinators**: Serial communication management
- **Client Coordinators**: Platform-specific client management

## Key Design Patterns

### 1. Singleton Pattern
The `Landscape` class implements a thread-safe singleton with factory override support:

```python
def __new__(cls):
    if Landscape.landscape_type is None:
        if Landscape.instance is None:
            Landscape.instance = super(Landscape, cls).__new__(cls)
    elif Landscape.instance is None:
        Landscape.instance = super(Landscape, cls.landscape_type).__new__(cls.landscape_type)
    return Landscape.instance
```

### 2. Factory Pattern
Resource and integration factories provide automated creation and registration:

```python
@testbase.register.resource_factory()
def create_landscape(constraints={}) -> Generator[Landscape, None, None]:
    lscape = LandscapeSingleton()
    yield lscape

@testbase.register.integration_factory()
def create_linux_client_coordinator_coupling() -> Generator[LinuxClientCoordinatorCoupling, None, None]:
    lc_coupling = LinuxClientCoordinatorCoupling()
    yield lc_coupling
```

### 3. Coordinator Pattern
Specialized coordinators manage different device types and protocols:

```python
class CoordinatorBase:
    def activate(self, activation_params): # Device activation
    def establish_connectivity(self, activation_params): # Connectivity
    def verify_connectivity(self, cmd, user, raiseerror): # Verification
    def create_landscape_device(self, landscape, device_info): # Device creation
```

### 4. Extension Pattern
Devices can be enhanced with protocol-specific extensions using weak references:

```python
def attach_extension(self, ext_type: str, extension: ProtocolExtension):
    if ext_type not in self._extensions:
        self._extensions[ext_type] = extension
    
class ProtocolExtension:
    def initialize(self, coord_ref: weakref.ReferenceType, extends_ref: weakref.ReferenceType,
                   extid: str, location: str, configinfo: dict):
        self._coord_ref = coord_ref
        self._extends_ref = extends_ref
```

### 5. Layer Pattern
Functionality is separated into five distinct layers with clear responsibilities:

- Installation → Configuration → Integration → Operations → Topology
- Each layer builds upon the previous layer
- Clear separation of concerns with well-defined interfaces

### 6. Pool Pattern
Resource pooling for exclusive access management:

```python
class LandscapeOperationalLayer:
    def checkout_device(self, device: LandscapeDevice):
        # Move from available pool to outstanding pool
    def checkin_device(self, device: LandscapeDevice):
        # Move from outstanding pool back to available pool
```

### 7. Coupling Pattern
Integration couplings provide extensible integration points:

```python
class CoordinatorCoupling(IntegrationCoupling):
    @classmethod
    def create_coordinator(cls, landscape: "Landscape") -> object:
        # Factory method for coordinator creation
```

### 8. Identifier Pattern
Friendly identifiers provide flexible device naming:

```python
class FriendlyIdentifier:
    def __init__(self, full_identifier: str, hint: str, identity_match: Optional[Union[re.Pattern, str]]=None):
        # Support for full names, hints, and regex matching
```

## Integration Points

### TestBase Framework Integration
- Resource factories for landscape creation
- Integration factories for coordinator couplings
- Feature attachment system for filtering
- Test resource management with checkout/checkin
- Constraint-based resource selection

### Credential Management
- Centralized credential manager singleton
- Per-device credential assignment
- Multiple credential types (SSH, etc.)
- Secure credential storage and retrieval
- Credential categories for organization

### Logging and Monitoring
- Enhanced logging throughout the system
- Configuration recording for debugging (YAML/JSON)
- Status verification and monitoring callbacks
- Error reporting and diagnostics
- Contact timestamp tracking

### Orchestration Integration
- **OrchestrationJob**: Base class for automation jobs
- **Job Phases**: Discovery, resource collection, configuration
- **Runtime Integration**: Build information and pipeline metadata
- **Job Requirements**: Landscape, topology, runtime, credentials

## Extensibility

### Adding New Device Types
1. Create device class inheriting from `LandscapeDevice` or platform-specific base (e.g., `ClientBase`, `NodeBase`)
2. Implement coordinator class inheriting from `CoordinatorBase` or specialized base
3. Create coordinator coupling for integration with proper integration keys
4. Register factory for automatic discovery using `@testbase.register.integration_factory()`

### Adding New Protocols
1. Create protocol extension inheriting from `ProtocolExtension`
2. Implement protocol-specific functionality with weak reference management
3. Register extension type in `DeviceExtensionType` enumeration
4. Attach to devices through coordinators during device creation

### Adding New Platforms
1. Create platform-specific client class inheriting from `ClientBase`
2. Implement platform-specific extensions (commands, configuration, etc.)
3. Create coordinator inheriting from `ClientCoordinatorBase`
4. Create coupling class and register integration factories
5. Implement SSH agent creation if required

### Adding New Services
1. Create service class inheriting from `LandscapeService` or `ServiceBase`
2. Implement service coordinator inheriting from `ServiceCoordinatorBase`
3. Create service coupling for integration
4. Register appropriate factories for discovery

### Factory Protocol Extension
- **LandscapingFactoryProtocol**: Defines extension points for landscape types
- **Super Factory Integration**: Configurable factory override system
- **Integration Coupling Discovery**: Automatic coupling type loading

## Configuration Schema

### Landscape Configuration
```yaml
apod:
  devices:
    - deviceType: "network/ssh"
      host: "device.example.com"
      credentials: ["ssh-cred"]
      name: "test-device"
      role: "worker"
      group: "cluster/primary"
      features:
        power: true
        serial: false
      users:
        admin: "admin-user"
      port: 22
      pty_params:
        timeout: 30
  power:
    - powerType: "network/dlipower"
      host: "power.example.com"
      credentials: ["power-cred"]
  serial:
    - serialType: "network/tcpserial"
      host: "serial.example.com"
      port: 2000

infrastructure:
  services:
    - serviceType: "vmware/vcenter"
      host: "vcenter.example.com"
      credentials: ["vcenter-cred"]
      name: "primary-vcenter"
      group: "vmware-services"
```

### Topology Configuration
```yaml
topology:
  networks:
    - name: "test-network"
      subnet: "192.168.1.0/24"
  clusters:
    - name: "primary-cluster"
      group: "cluster/primary"
      nodes:
        - "node1"
        - "node2" 
        - "node3"
      spares:
        - "spare1"
```

### Integration Classes
```python
INTEGRATION_CLASS_NETWORK_SSH = "network/ssh"
INTEGRATION_CLASS_NETWORK_UPNP = "network/upnp"
INTEGRATION_CLASS_NETWORK_DLIPOWER = "network/dlipower"
INTEGRATION_CLASS_NETWORK_TCPSERIAL = "network/tcpserial"
```

## Testing Integration

### Resource Management
- Devices and services can be checked out/in for exclusive access
- Resource pools prevent conflicts between concurrent tests
- Automatic cleanup and resource release
- Cluster-level checkout/checkin for coordinated resource access
- Outstanding vs available resource tracking

### Test Factories
- Landscape factory provides global landscape instance
- Integration factories register coordinators and couplings
- Constraint-based resource selection
- AutomationPod integration for test environment access

### Feature-Based Filtering
- Devices and services support feature tags
- Include/exclude filters for resource selection
- Dynamic filtering based on test requirements
- Filter types: by device type, role, name, group
- Consistent filtering interfaces for devices and services

### Filter Implementations
```python
class IncludeDeviceByDeviceType(IncludeDeviceBase):
    # Filters devices by device type
class IncludeDeviceByRole(IncludeDeviceBase):
    # Filters devices by assigned role
class IncludeDeviceByGroup(IncludeDeviceBase):
    # Filters devices by group membership
class IncludeServiceByName(IncludeServiceBase):
    # Filters services by name
```

## Error Handling and Diagnostics

### Validation Framework
- Multi-level configuration validation with integration coupling participation
- Error and warning collection with detailed context
- Detailed error reporting with configuration snippets
- Validation phases: landscape, topology, device, service configurations

### Status Verification
- Protocol-specific status verification callbacks
- Connectivity testing and validation through coordinators
- Health monitoring and reporting with timestamp tracking
- Device enhancement and metadata validation

### Logging and Debugging
- Enhanced logging with structured output throughout all components
- Configuration recording for debugging (YAML and JSON formats)
- Runtime state capture and analysis
- Error formatting with configuration context

### Exception Management
- **CheckinError**: Resource checkin validation errors
- **CheckoutError**: Resource checkout validation errors  
- **ConfigurationError**: Configuration validation failures
- **SemanticError**: Logic and semantic validation errors
- Comprehensive error context with device/service information

## Performance Considerations

### Lazy Initialization
- Resources initialized only when needed
- Deferred connectivity establishment
- On-demand device enhancement and metadata loading
- Activation parameter control for selective initialization

### Caching
- IP address resolution caching in devices
- Configuration caching and reuse
- Credential caching for performance
- Device and service lookup caching

### Concurrent Operations
- Thread-safe operations throughout with individual locks
- Parallel device initialization through coordinators
- Concurrent connectivity testing and verification
- Lock scope management for nested operations

### Resource Pool Optimization
- Efficient device and cluster pool management
- Fast lookup tables for device/service resolution
- Optimized checkout/checkin operations with validation

## Security Considerations

### Credential Management
- Secure credential storage and retrieval through centralized manager
- Per-device credential isolation and assignment
- Multiple authentication methods (SSH, etc.)
- Credential categories for organized access control

### Network Security
- Secure protocol implementations (SSH with configurable parameters)
- Certificate validation and management
- Encrypted communications through protocol extensions
- Configurable SSH ports and PTY parameters

### Access Control
- Resource checkout/checkin for exclusive access control
- Device isolation capabilities through configuration
- Feature-based access restrictions
- Thread-safe resource pool management preventing unauthorized access

## Future Extensibility

The architecture is designed to support:
- Additional device types and platforms through inheritance patterns
- New communication protocols via the extension system
- Enhanced monitoring and diagnostics through callback systems
- Cloud and container integration via service coordinators
- Advanced orchestration capabilities through orchestration jobs
- Machine learning-based optimization through data collection points
- Specialized cluster types (beyond Raspberry Pi clusters)
- Additional VMware integrations (vSphere, Workstation extensions)
- Enhanced topology management and network modeling

### Extension Points
- **Factory Protocol System**: `LandscapingFactoryProtocol` for type overrides
- **Super Factory Integration**: Configurable factory override mechanisms
- **Integration Coupling System**: Hierarchical integration support
- **Protocol Extension Framework**: Weak reference-based extension management
- **Coordinator Specialization**: Platform and protocol-specific coordinators

## Advanced Features

### Automation Pod Integration
- **AutomationPod**: Provides access to global landscape instance
- **Configuration Coupling**: Integration with TestBase framework
- **Resource Access**: Simplified landscape access for automation scripts

### Friendly Identifier System
- **Flexible Naming**: Support for full identifiers, hints, and regex matching
- **Identity Resolution**: Automatic identity extraction from full identifiers
- **Relationship Tracking**: Clear mapping between hints and full identifiers
- **Dynamic Updates**: Support for identifier updates during discovery

### Configuration Extraction and Export
- **Selective Export**: Filter-based configuration extraction
- **Format Preservation**: Maintains original configuration structure
- **Deep Copying**: Prevents configuration corruption during extraction
- **Multi-Type Support**: Device, service, and cluster configuration export

### Orchestration Framework
- **Job Lifecycle**: Structured execution phases with proper sequencing
- **Runtime Integration**: Build and pipeline metadata integration
- **Resource Collection**: Automated resource discovery and collection
- **Configuration Management**: Landscape, topology, and runtime requirements

## Implementation Highlights

### Thread Safety Architecture
- **Landscape Lock**: Global RLock for landscape-wide operations
- **Individual Locks**: Per-device, per-service, per-coordinator locking
- **Scope Management**: Context managers for safe lock acquisition/release
- **Initialization Gates**: Thread-safe singleton initialization with gates

### Resource Pool Management
- **Dual Pool System**: Available vs outstanding resource tracking
- **Cluster Support**: Coordinated cluster checkout/checkin operations
- **Validation**: Comprehensive validation during checkout/checkin operations
- **Error Handling**: Detailed error reporting for pool state issues

### Integration Coupling System
- **Hierarchical Couplings**: Support for nested integration relationships
- **Dependency Registration**: Integration dependency management
- **Factory Integration**: Automated coupling discovery and registration
- **Key-Based Lookup**: Structured integration keys for coupling identification

## Conclusion

The AutoMojo Landscaping package provides a sophisticated, enterprise-grade framework for test automation across diverse environments. Its five-layer architecture, comprehensive device and service management, advanced clustering capabilities, and extensive integration points make it suitable for complex automation scenarios including:

- Multi-platform device coordination (Linux, macOS, Windows)
- Cluster computing environments with node management
- Protocol-diverse environments (SSH, Serial, Power, UPNP, REST)
- Service integration (VMware, cloud services)
- Orchestrated automation workflows
- Resource pooling and exclusive access management

The framework maintains simplicity for basic use cases while providing the extensibility and robustness required for enterprise automation environments. Its thread-safe design, comprehensive error handling, and extensive logging capabilities ensure reliable operation in production environments.