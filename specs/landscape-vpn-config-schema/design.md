# Design

## Overview

This feature adds the `vpn:` section to `landscape.yaml` and the per-device
`devices[*].vpn:` override. The schema is parsed at landscape load time and
materialised into the existing landscape coordinator constructs: a list of
VPN provider objects on the landscape root and a populated
`preferred_plane` plus optional provider reference on each `LandscapeDevice`.

The schema validation lives here so every consumer — landscaping itself,
`automojo-provisioning` (which writes `landscape.yaml` after `apply`), and
`automojo-arcli` (`arcli landscape validate`) — shares one parser. Diagnostic
output is structured (`LandscapeConfigDiagnostic`) so editor integrations can
surface line / column information without re-parsing.

**See Also:**
- [device-address-set](../device-address-set/design.md)
- [vpn-coordinator-coupling](../vpn-coordinator-coupling/design.md) — the
  consumer that constructs from parsed provider entries.
- automojo-configuration `vpn-config-schema` spec — the cross-package YAML
  schema authoring counterpart.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│   landscape.yaml                                             │
│                                                              │
│   vpn:                                                       │
│     default_plane: OVERLAY                                   │
│     providers:                                               │
│       - name: corp-tailnet                                   │
│         kind: tailscale                                      │
│         credential_ref: tailscale:corp                       │
│         tailnet: corp.example.com                            │
│         default_tags: [tag:lab]                              │
│                                                              │
│   devices:                                                   │
│     - name: db01                                             │
│       vpn:                                                   │
│         provider: corp-tailnet                               │
│         managed: true                                        │
│         preferred_plane: OVERLAY                             │
└──────────────────────────────┬───────────────────────────────┘
                               │ load + validate
                               ▼
┌──────────────────────────────────────────────────────────────┐
│             LandscapeRoot                                    │
│   vpn_providers: List[VPNProviderEntry]                      │
│   default_plane: AddressPlane                                │
│                                                              │
│             LandscapeDevice                                  │
│   vpn_provider: Optional[str]                                │
│   vpn_managed: bool                                          │
│   vpn_advertise_tags: List[str]                              │
│   preferred_plane: AddressPlane                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Model

```python
@dataclass
class VPNProviderEntry:
    name: str
    kind: str                       # "tailscale" | "twingate"
    credential_ref: str
    tailnet: Optional[str]
    network_slug: Optional[str]
    default_tags: List[str]

@dataclass
class LandscapeConfigDiagnostic:
    severity: str                   # "error" | "warning"
    path: str                       # e.g., "vpn.providers[1].kind"
    message: str
    line: Optional[int]
    column: Optional[int]

class LandscapeConfigError(Exception):
    """Raised when the vpn: block contains a hard error."""
```

---

## Module Layout

```
source/packages/automojo/landscaping/config/
├── vpnconfigschema.py            ← schema constants, validate_*
├── vpnproviderentry.py
└── landscapeconfigdiagnostic.py
```

Tests:

```
source/testroots/.../landscaping/config/
├── test_vpnconfigschema.py
└── fixtures/
    ├── landscape_no_vpn.yaml
    ├── landscape_tailscale_only.yaml
    ├── landscape_per_device_overrides.yaml
    └── landscape_invalid_kind.yaml
```

---

## Validation Algorithm

`validate_landscape_vpn_block(doc)`:

1. If `doc.get("vpn")` is absent → return `[]`.
2. Validate `vpn.default_plane` is one of the enum values; otherwise append
   an `error` diagnostic.
3. For each `vpn.providers[i]`:
   - Required keys present (`name`, `kind`, `credential_ref`)?
   - `kind` ∈ {`tailscale`, `twingate`}?
   - If `tailscale`, `tailnet` is non-empty?
   - If `twingate`, `network_slug` is non-empty?
   - Unknown keys → `warning`.
4. For each `devices[i].vpn`:
   - `provider` references a defined root provider → else `error`.
   - `preferred_plane` is a valid enum value → else `error`.
   - Unknown keys → `warning`.
5. Return the accumulated diagnostics.

The loader (separate from the validator) calls
`validate_landscape_vpn_block`, fails fast on any `error` diagnostic, and
logs each `warning` once.

---

## Backwards Compatibility

- Loaders MUST accept landscapes with no `vpn:` block and produce
  zero-element `vpn_providers` lists.
- Existing devices without `vpn:` entries inherit `preferred_plane=PUBLIC`
  and `vpn_provider=None`.
- No existing landscape file requires modification.

---

## Testing Strategy

- Example tests exercise the four fixture files plus inline doc snippets:
  - No `vpn:` block → empty diagnostics, default plane = PUBLIC.
  - Tailscale-only landscape → one provider parsed, device defaults
    populated.
  - Per-device overrides → device.preferred_plane reflects the override.
  - Invalid `kind` → error diagnostic with `path="vpn.providers[0].kind"`.
  - Unknown key → warning diagnostic, no error.
  - Device referencing a non-existent provider → error diagnostic.
- Validator function tests cover each diagnostic path independently.
- A regression test asserts that loading every existing landscape fixture in
  `automojo-landscaping/source/testroots/.../fixtures/` produces no new
  diagnostics post-feature.
