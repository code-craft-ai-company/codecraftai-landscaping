# Requirements

## Introduction

The `vpn-coordinator-coupling` feature adds `VPNCoordinatorCoupling` under
`automojo/landscaping/coupling/`. It is the landscape-side glue that
discovers peer devices from a VPN control plane (Tailscale or Twingate) and
attaches overlay addresses to the matching `LandscapeDevice` records in the
landscape. Where the landscape's host policy requires it, it also registers
an `IVPNClient` to drive a local daemon for bring-up / status / down on the
host.

The coupling sits beside the existing landscape couplings (SSH, DNS, power)
and follows the same pattern: it is constructed from credentials and config,
it accepts `aspects` on every behaviour-bearing call, and it is idempotent
so re-couplings are no-ops when state already matches.

All methods take named parameters. No `@retry` or other behaviour-modifying
decorators are used.

---

## Requirements

### Requirement 1: Attach Overlay Addresses by Hostname Match

**User Story:** As a landscape coordinator, I want every landscape device
that exists in the tailnet to have its overlay address populated so SSH /
DNS / file-ops can choose it via plane selection.

#### Acceptance Criteria

1. WHEN `couple(devices, aspects)` is called THE SYSTEM SHALL invoke
   `control_plane.list_devices(aspects)` once and SHALL build a
   `{normalised_hostname → VPNDeviceRecord}` index.
2. WHEN a `LandscapeDevice` has a hostname that matches an entry in the
   index THE SYSTEM SHALL call `device.addresses.set_overlay(provider,
   record.addresses[0])`.
3. WHEN a `LandscapeDevice` has a `tag` matching any entry in
   `record.tags` AND no hostname match exists THE SYSTEM SHALL use the tag
   match.
4. WHEN both hostname and tag match different records THE SYSTEM SHALL
   prefer the hostname match and SHALL log at INFO that the tag match was
   superseded.
5. WHEN a device has no match in either index THE SYSTEM SHALL leave the
   overlay slot unchanged and log at DEBUG.

### Requirement 2: Tag-Based Match Disambiguation

**User Story:** As a landscape designer, I want tag-based matches to be
unambiguous so deterministic coupling is preserved.

#### Acceptance Criteria

1. IF a device's `tag` matches multiple `VPNDeviceRecord`s THEN THE SYSTEM
   SHALL raise `VPNCoordinatorAmbiguousMatchError` listing every candidate
   record id and asking the operator to disambiguate via hostname.
2. THE SYSTEM SHALL NOT pick one record silently.

### Requirement 3: Register Local VPN Client For Managed Hosts

**User Story:** As a landscape operator, I want landscape-managed hosts that
should join the mesh to have a local-daemon client registered so subsequent
landscape operations can bring the daemon up/down.

#### Acceptance Criteria

1. WHEN the landscape declares a host as `vpn.managed=True` THE SYSTEM SHALL
   construct an `IVPNClient` of the configured provider, wire it to the
   device's runner, and register it on the device under
   `device.vpn_client_for(provider)`.
2. WHERE no provider-matching credential is configured THE SYSTEM SHALL raise
   `ConfigurationError` with the provider name and the credential namespace
   that was missing.

### Requirement 4: Aspects on Coupling Calls

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsLandscapeCoupling` on `couple`,
   `decouple`, and `refresh`, defaulting to
   `DEFAULT_LANDSCAPE_COUPLING_ASPECTS`.
2. THE SYSTEM SHALL NOT use behaviour-modifying decorators.

### Requirement 5: Idempotent Re-Coupling

#### Acceptance Criteria

1. WHEN `couple(...)` is called twice in succession with no upstream change
   THE SYSTEM SHALL produce no further mutations on any landscape device
   address set and SHALL return a result indicating zero updates.
2. THE SYSTEM SHALL surface a count of `updated`, `skipped`, and
   `unmatched` devices in the returned `VPNCouplingResult`.

### Requirement 6: Decoupling Clears Overlay Addresses

#### Acceptance Criteria

1. WHEN `decouple(devices, aspects)` is called THE SYSTEM SHALL clear the
   overlay slot for the configured provider on every passed device.
2. THE SYSTEM SHALL NOT touch the PUBLIC or PRIVATE slots.
