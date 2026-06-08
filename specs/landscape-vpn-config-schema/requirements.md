# Requirements

## Introduction

The `landscape-vpn-config-schema` feature adds a top-level `vpn:` section to
`landscape.yaml` along with per-device `vpn:` overrides. The schema lists VPN
providers, references credentials by name (resolved through
`codecraftai-credentials`), declares a default landscape-wide preferred plane,
and per-device opt-in for `managed=True` daemon ownership.

Schema validation lives in this feature so every consumer (landscaping,
provisioning, arcli) shares one parser. The schema is documented as
forward-compatible — unknown provider kinds are an error, unknown leaf keys
are a warning.

All schema validation paths take named parameters. No behaviour-modifying
decorators.

---

## Requirements

### Requirement 1: Root-Level `vpn:` Block

**User Story:** As a landscape designer, I want a single block at the top of
`landscape.yaml` to declare every VPN provider the landscape uses so per-device
overrides only need to reference a provider by name.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept a top-level optional `vpn:` mapping with the
   schema:

   ```yaml
   vpn:
     default_plane: PUBLIC | PRIVATE | OVERLAY
     providers:
       - name: <str>
         kind: tailscale | twingate
         credential_ref: <credential namespace>
         tailnet: <str>             # tailscale only
         network_slug: <str>        # twingate only
         default_tags: [<str>, ...]
   ```

2. WHEN `vpn:` is absent THE SYSTEM SHALL default `default_plane` to
   `PUBLIC` and SHALL register zero VPN providers.
3. IF `providers[*].kind` is not in the accepted set THEN THE SYSTEM SHALL
   raise `LandscapeConfigError`.
4. IF `providers[*].credential_ref` does not resolve in
   `CredentialManager` THEN THE SYSTEM SHALL raise `ConfigurationError`
   listing the missing credential namespace.

### Requirement 2: Per-Device `vpn:` Override

**User Story:** As a landscape designer, I want to opt specific devices in to
the overlay plane and to declare per-device VPN ownership.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept an optional `vpn:` mapping under each
   `devices[*]` entry:

   ```yaml
   devices:
     - name: db01
       vpn:
         provider: <provider name>     # must reference one in root vpn.providers
         managed: <bool>               # default False
         advertise_tags: [<str>, ...]  # override root default_tags
         preferred_plane: PUBLIC | PRIVATE | OVERLAY
   ```

2. WHEN `vpn.provider` does not match a root-declared provider THE SYSTEM
   SHALL raise `LandscapeConfigError`.
3. WHEN `vpn.preferred_plane` is set THE SYSTEM SHALL override the root
   `default_plane` for this device only.

### Requirement 3: Plane Default Resolution

#### Acceptance Criteria

1. WHEN a device declares `vpn.preferred_plane` THE SYSTEM SHALL use that
   value as the device's `preferred_plane`.
2. WHEN a device does not declare `vpn.preferred_plane` AND the root
   `vpn.default_plane` is set THE SYSTEM SHALL use the root value.
3. WHEN neither is set THE SYSTEM SHALL default to `PUBLIC`.

### Requirement 4: Unknown Key Tolerance

#### Acceptance Criteria

1. WHEN an unknown leaf key appears under `vpn:` or `devices[*].vpn:` THE
   SYSTEM SHALL log a WARNING with the file path and key name and SHALL
   proceed.
2. WHEN an unknown top-level key appears at the root THE SYSTEM SHALL NOT
   alter behaviour — existing landscape root-key tolerance applies.

### Requirement 5: Validation Surface

#### Acceptance Criteria

1. THE SYSTEM SHALL expose a public function
   `validate_landscape_vpn_block(*, doc) -> List[LandscapeConfigDiagnostic]`
   so arcli, provisioning, and editor tooling can validate without loading a
   live landscape.
2. THE SYSTEM SHALL return an empty list when the block is valid.

### Requirement 6: Backwards Compatibility

#### Acceptance Criteria

1. WHEN a landscape file with no `vpn:` block is loaded THE SYSTEM SHALL
   behave exactly as before this feature landed.
2. THE SYSTEM SHALL NOT require any existing landscape file to change.
