# Requirements

## Introduction

The `device-address-set` feature replaces the single-string `_host` field
historically held by `LandscapeDevice` and its peers with a typed
`DeviceAddressSet` that holds a map of `AddressPlane → address`. The set
exposes explicit accessors (`public()`, `private()`, `overlay(provider=None)`)
and a single `resolve(plane, fallback_planes=None)` entry point consumed by
the SSH, DNS, and file-ops interop layers.

This object is the central pivot between mesh-VPN awareness in the interop
layer and the existing landscape resolution path. The resolution semantics
must be total and deterministic so that every caller — `SSHBase`,
`OverlayDNSResolver`, the file operator — observes the same answer for the
same `(set, plane, fallback)` triple. The feature therefore requires
`hypothesis` property tests covering the full plane-priority semantics for
any combination of present/absent planes.

All public methods take named parameters. No behaviour-modifying decorators.

---

## Requirements

### Requirement 1: Hold Addresses Per Plane

**User Story:** As a landscape designer, I want a single object to hold a
device's reachable addresses across all planes so I never pass loose strings
around.

#### Acceptance Criteria

1. THE SYSTEM SHALL provide `DeviceAddressSet` with internal storage mapping
   `AddressPlane → Optional[str]` for `PUBLIC` and `PRIVATE`, and
   `AddressPlane.OVERLAY → Dict[str, Optional[str]]` keyed by provider name.
2. THE SYSTEM SHALL initialise every plane absent (`None` / `{}`) by default.
3. THE SYSTEM SHALL provide named-parameter setters: `set_public(address)`,
   `set_private(address)`, `set_overlay(provider, address)`.
4. THE SYSTEM SHALL provide named-parameter accessors: `public()`,
   `private()`, `overlay(provider=None)`.
5. WHERE `overlay(provider=None)` is called AND multiple providers are
   present THE SYSTEM SHALL return the address for the first
   provider in insertion order; this behaviour SHALL be documented.

### Requirement 2: Total, Deterministic Resolution

**User Story:** As an interop client, I want `resolve(plane, fallback_planes)`
to be a total, pure function so my behaviour matches what callers expect.

#### Acceptance Criteria

1. THE SYSTEM SHALL provide `resolve(*, plane, fallback_planes=None)` that
   returns `Optional[str]` and never raises.
2. WHEN the requested `plane` resolves to a non-empty string THE SYSTEM SHALL
   return that string.
3. WHEN the requested `plane` is absent AND `fallback_planes` is non-empty
   THE SYSTEM SHALL try each fallback plane in declared order, returning the
   first non-empty address.
4. WHEN every requested plane is absent THE SYSTEM SHALL return `None`.
5. THE SYSTEM SHALL be deterministic — same input, same output, across runs
   and across processes.

### Requirement 3: Empty Strings Treated As Absent

**User Story:** As an interop caller, I want empty-string addresses ignored so
upstream data quirks do not produce nonsense dial targets.

#### Acceptance Criteria

1. WHEN an address is set to `""` THE SYSTEM SHALL treat it as absent in
   `resolve(...)` and the per-plane accessors.
2. THE SYSTEM SHALL NOT raise on empty-string input — the setter accepts it
   to preserve round-trip compatibility with YAML loaders that emit `""`.

### Requirement 4: `IDeviceAddressSet` Protocol

#### Acceptance Criteria

1. THE SYSTEM SHALL define `IDeviceAddressSet` in `automojo-interfaces`
   exposing `public()`, `private()`, `overlay(provider)`, and
   `resolve(plane, fallback_planes)`.
2. `DeviceAddressSet` SHALL implement `IDeviceAddressSet`.
3. WHEN a consumer (SSH client, DNS resolver, file operator) accepts an
   address bundle THE SYSTEM SHALL type-hint the parameter as
   `IDeviceAddressSet`, never the concrete class.

### Requirement 5: `preferred_plane` on Device and Landscape

#### Acceptance Criteria

1. THE SYSTEM SHALL add `preferred_plane: AddressPlane` to `LandscapeDevice`
   with default `AddressPlane.PUBLIC`.
2. THE SYSTEM SHALL allow the landscape root config to declare a
   landscape-wide `preferred_plane`; per-device values SHALL override.
3. WHEN a device has `preferred_plane=OVERLAY` AND no overlay address THE
   SYSTEM SHALL log a single WARNING per process per device noting the
   misconfiguration.

### Requirement 6: Property Tests

#### Acceptance Criteria

1. THE SYSTEM SHALL include `hypothesis` property tests asserting:
   - For any randomly generated `(planes_present, preferred, fallback_list)`
     fixture, `resolve(...)` either returns an address contained in the set
     or returns `None`. No other outcome is possible.
   - `resolve(...)` is deterministic — two invocations with the same input
     return the same value.
   - `resolve(plane=p, fallback_planes=None)` returns
     `address_set.public()` when `p == PUBLIC and PUBLIC ∈ planes_present`.
   - Identity under fallback: `resolve(plane=p, fallback_planes=[p])`
     returns the same value as `resolve(plane=p)`.
   - Fall-through stops at the first present plane in the priority list.
