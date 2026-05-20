# Design

## Overview

`VPNCoordinatorCoupling` is the landscape-side coupling that wires a VPN
control plane and (optionally) a local VPN daemon into the landscape's device
records. It is constructed from a credential + control-plane client + provider
name, and its primary verb `couple(...)` walks the configured landscape
devices, matches each against the control-plane device list, and populates the
overlay slot of every matched device's `DeviceAddressSet`.

The coupling lives next to the existing landscape couplings (SSH, DNS, power,
etc.) and follows the same lifecycle: construct → couple → use → optionally
refresh → decouple. It is idempotent, so re-running `couple(...)` is safe and
cheap.

**See Also:**
- [device-address-set](../device-address-set/design.md) — the structure the
  coupling populates.
- [landscape-vpn-config-schema](../landscape-vpn-config-schema/design.md) —
  the YAML block that configures this coupling.
- [vpn-tailscale-control-plane](../../../automojo-interop/specs/vpn-tailscale-control-plane/design.md)
- [vpn-twingate-control-plane](../../../automojo-interop/specs/vpn-twingate-control-plane/design.md)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                LandscapeCoordinator                          │
│  - constructs couplings from landscape config                │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│              VPNCoordinatorCoupling                          │
│  landscaping/coupling/vpncoordinatorcoupling.py              │
│                                                              │
│  couple(devices, aspects)     → VPNCouplingResult            │
│  refresh(devices, aspects)    → VPNCouplingResult            │
│  decouple(devices, aspects)   → None                         │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             ▼                                ▼
   IVPNControlPlane                  IVPNClient (managed hosts)
   list_devices()                    bring_up / status / bring_down
```

---

## Data Model

```python
@dataclass
class VPNCouplingResult:
    provider: str
    updated: int
    skipped: int
    unmatched: int
    ambiguous_tag_matches: List[str]

class VPNCoordinatorAmbiguousMatchError(Exception):
    """Raised when a device tag matches more than one VPN device record."""

@dataclass
class AspectsLandscapeCoupling:
    refresh_interval_seconds: float = 30.0
    timeout_seconds: float = 60.0
    raise_on_ambiguous: bool = True

DEFAULT_LANDSCAPE_COUPLING_ASPECTS = AspectsLandscapeCoupling()
```

---

## Module Layout

```
source/packages/automojo/landscaping/coupling/
├── __init__.py
├── vpncoordinatorcoupling.py
├── vpncouplingresult.py
└── exceptions.py
```

Tests:

```
source/testroots/.../landscaping/coupling/
├── test_vpncoordinatorcoupling.py
└── fixtures/
    ├── control_plane_devices.json
    └── landscape_with_tags.yaml
```

---

## Matching Algorithm

1. Normalise: lowercase the device hostname and every VPN record hostname.
2. Build a `{lower_hostname → record}` index.
3. For each landscape device:
   - If `hostname` matches the index, attach `record.addresses[0]` to the
     overlay slot.
   - Else, iterate device tags. For each tag, find every VPN record whose
     `tags` list contains it.
     - 0 matches → unmatched.
     - 1 match → attach overlay.
     - >1 matches → `VPNCoordinatorAmbiguousMatchError` (raised when
       `aspects.raise_on_ambiguous=True`) or recorded in
       `result.ambiguous_tag_matches` for operator review when `False`.
4. Increment counters (`updated`, `skipped`, `unmatched`) and return the
   `VPNCouplingResult`.

`set_overlay(provider, address)` is called only when the new address differs
from the existing one, preserving idempotency.

---

## Managed-Host Path

When the landscape declares a host with `vpn.managed=True`:

1. Look up the provider credential from the registered
   `CredentialManager` namespace (e.g., `tailscale:default`).
2. Construct the matching `IVPNClient` subclass
   (`TailscaleClient` / `TwingateClient`) with the device's existing runner.
3. Register the client on the device under
   `device.vpn_client_for(provider)`.

The coupling never calls `bring_up()` itself — that is owned by the
sysman maintenance coordinator. The coupling only makes the client
available so other coordinators can drive it.

---

## Testing Strategy

- Fake `IVPNControlPlane` returns a canned device list.
- Fake `LandscapeDevice` exposes `hostname`, `tags`, and a real
  `DeviceAddressSet`.
- Example tests:
  - Hostname match attaches the overlay address.
  - Tag match (single) attaches the overlay address.
  - Tag match (multiple) raises `VPNCoordinatorAmbiguousMatchError` when
    `aspects.raise_on_ambiguous=True`; records and continues when `False`.
  - Hostname-and-tag conflict prefers hostname and logs at INFO.
  - Unmatched device leaves the overlay slot unchanged.
  - Idempotency: second `couple(...)` call returns `updated=0`.
  - Decouple clears only the overlay slot.
  - Managed host without credential raises `ConfigurationError`.
- No test requires a live tailnet / Twingate network.
- Coverage assertion: every branch of the matching algorithm has at least one
  dedicated test.
