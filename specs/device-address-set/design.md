# Design

## Overview

`DeviceAddressSet` is the canonical multi-plane address container for
`LandscapeDevice`. It implements `IDeviceAddressSet` from
`codecraftai-interfaces` and is the only legal way to hand a host to SSH, DNS,
or file-ops in the post-refactor landscape model. The single-string `_host`
attribute is removed (not deprecated) as part of this work; consumers must
migrate to the address set.

Resolution is implemented as a pure, total function over the set's internal
state and the caller-supplied `(plane, fallback_planes)` pair. Property tests
under `hypothesis` cover plane priority across every combination of
present/absent planes.

**See Also:**
- codecraftai-interfaces `address-plane-types` spec — defines `AddressPlane`
  and `IDeviceAddressSet`.
- [ssh-address-plane-awareness](../../../codecraftai-interop/specs/ssh-address-plane-awareness/design.md)
  — consumes `resolve(...)`.
- [overlay-dns-resolver](../../../codecraftai-interop/specs/overlay-dns-resolver/design.md)
  — uses overlay addresses for resolution.
- [vpn-coordinator-coupling](../vpn-coordinator-coupling/design.md) —
  populates the overlay slot via the VPN control plane.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    LandscapeDevice                           │
│   addresses: DeviceAddressSet  ◄── replaces _host string     │
│   preferred_plane: AddressPlane                              │
└──────────────────────────────┬───────────────────────────────┘
                               │ IDeviceAddressSet
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                   DeviceAddressSet                           │
│  addressing/deviceaddressset.py                              │
│                                                              │
│  _public: Optional[str]                                      │
│  _private: Optional[str]                                     │
│  _overlay: Dict[str, Optional[str]]   # provider → address   │
│                                                              │
│  public()                            → Optional[str]         │
│  private()                           → Optional[str]         │
│  overlay(provider=None)              → Optional[str]         │
│  resolve(plane, fallback_planes)     → Optional[str]         │
│  set_public(address)                                         │
│  set_private(address)                                        │
│  set_overlay(provider, address)                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Model

```python
class DeviceAddressSet(IDeviceAddressSet):
    def __init__(
        self,
        *,
        public: Optional[str] = None,
        private: Optional[str] = None,
        overlay: Optional[Dict[str, Optional[str]]] = None,
    ) -> None:
        self._public = public
        self._private = private
        self._overlay = dict(overlay) if overlay is not None else {}

    def public(self) -> Optional[str]: ...
    def private(self) -> Optional[str]: ...
    def overlay(self, *, provider: Optional[str] = None) -> Optional[str]: ...
    def resolve(
        self,
        *,
        plane: AddressPlane,
        fallback_planes: Optional[List[AddressPlane]] = None,
    ) -> Optional[str]: ...
```

Empty-string addresses are stored as supplied and filtered to `None` by the
accessors. The constructor never raises on empty strings; the accessors
never return empty strings.

---

## Resolution Algorithm (pure)

```
def resolve(plane, fallback_planes):
    attempted = [plane] + (fallback_planes or [])
    for p in attempted:
        candidate = _get_plane(p)
        if candidate is not None and len(candidate) > 0:
            return candidate
    return None
```

Totality: the function always returns either a non-empty string or `None`.
The empty-string filter is applied uniformly so the contract holds even for
malformed upstream YAML.

---

## Module Layout

```
source/packages/ccai/landscaping/addressing/
├── __init__.py
└── deviceaddressset.py    ← class + free helpers

source/packages/ccai/landscaping/
└── landscapedevice.py     ← now uses DeviceAddressSet (see _resolve_addresses)
```

Tests:

```
source/testroots/.../landscaping/addressing/
├── test_deviceaddressset.py
└── property/
    └── test_deviceaddressset_properties.py    ← hypothesis
```

---

## `LandscapeDevice` Refactor

`_resolve_ipaddress()` becomes `_resolve_addresses() -> DeviceAddressSet`.
The existing DNS/cloud-metadata code paths populate the PUBLIC and PRIVATE
slots; the overlay slot is populated by the new
`VPNCoordinatorCoupling` (see [vpn-coordinator-coupling](../vpn-coordinator-coupling/design.md)).
The old `_host` attribute is removed; any caller still using it gets a clear
`AttributeError` at import time.

`preferred_plane` is read from the device config (with the landscape root as
fallback) at landscape parse time and stored as a class attribute on
`LandscapeDevice`.

---

## Testing Strategy

- **Example tests:**
  - Constructor with each plane combination populates correctly.
  - Empty-string addresses returned as `None`.
  - `resolve(plane=PUBLIC)` returns the public address.
  - `resolve(plane=OVERLAY, fallback_planes=[PRIVATE, PUBLIC])` walks the
    priority list and returns the first present address.
  - `resolve(plane=OVERLAY)` on an empty overlay returns `None`.
  - `overlay(provider=None)` with multiple providers returns the
    first-inserted entry; with `provider="tailscale"` returns the named one.

- **Property tests (`hypothesis`):**
  - `test_resolve_returns_address_or_none`: for any generated set + plane +
    fallback, the return value is either `None` or an address that exists in
    the set under one of the attempted planes.
  - `test_resolve_is_deterministic`: invoking `resolve(...)` twice on the
    same set with the same arguments returns the same value.
  - `test_resolve_preferred_present`: when the preferred plane is present,
    `resolve` returns its address regardless of `fallback_planes`.
  - `test_resolve_fallback_walks_in_order`: when the preferred plane is
    absent, the returned address (if any) is the one belonging to the
    first present plane in the fallback list.
  - `test_resolve_total`: for every input the function returns `Optional[str]`
    and never raises.
  - `test_set_then_get_round_trip`: `set_overlay(p, addr); overlay(provider=p)`
    returns `addr` when `addr` is non-empty, `None` when empty.

- No test requires a live landscape, runner, or network.
