# Implementation Plan — Device Address Set

- [x] 1. Confirm `AddressPlane` enum and `IDeviceAddressSet` protocol are
  available from `codecraftai-interfaces` (per the `address-plane-types`
  feature in M1). If not, block on that spec.
- [x] 2. Create `ccai/landscaping/addressing/__init__.py`.
- [x] 3. Create `ccai/landscaping/addressing/deviceaddressset.py`:
  - [x] 3a. Constructor accepting named `public`, `private`, `overlay`.
  - [x] 3b. Setters `set_public`, `set_private`, `set_overlay`.
  - [x] 3c. Accessors `public()`, `private()`, `overlay(provider=None)`.
  - [x] 3d. `resolve(*, plane, fallback_planes=None)` pure function.
  - [x] 3e. Empty-string filtering inside accessors.
- [ ] 4. Refactor `ccai/landscaping/landscapedevice.py`:
  - [x] 4a. Add `addresses: DeviceAddressSet` instance attribute initialised
    in `__init__` per coding standards.
  - [x] 4b. Add `_resolve_addresses() -> DeviceAddressSet` alongside the
    existing `_resolve_ipaddress()`. NOTE (deviation from spec): the
    legacy `_resolve_ipaddress` method is preserved and now mirrors its
    result into the address set's PUBLIC slot — full replacement is
    deferred per the M4 "additive at the API boundary" mandate.
  - [ ] 4c. Remove the `_host` attribute and its property accessor.
    DEFERRED — backward compatibility is non-negotiable for this
    foundational M4 change. `_host` remains readable; downstream
    migration to `addresses.resolve(...)` will land in a follow-up.
    NOTE: this task is intentionally left deferred per the
    M4-COMPLETE.md backward-compat decision (keep `_host` as a shim for
    one release cycle).
  - [x] 4d. Add `preferred_plane: AddressPlane` instance attribute sourced
    from device config with landscape-root fallback, default
    `AddressPlane.PUBLIC`.
  - [x] 4e. Emit a one-shot WARNING when `preferred_plane=OVERLAY` and the
    overlay slot is empty after `_resolve_addresses()`.
- [ ] 5. Audit `landscaping/` for any remaining `_host` references and migrate
  each to `addresses.resolve(...)`. DEFERRED — see 4c.
  NOTE: this task is intentionally left deferred per the M4-COMPLETE.md
  backward-compat decision (keep `_host` as a shim for one release cycle).
- [x] 6. Apply project coding standards (named-only, explicit returns).
- [x] 7. Tests — example-based:
  - [x] 7a. Constructor with each plane combination.
  - [x] 7b. Empty-string address returns `None` from accessor.
  - [x] 7c. `resolve` priority order.
  - [x] 7d. `overlay(provider=None)` returns first-inserted entry.
  - [x] 7e. `LandscapeDevice` address-set surface populates PUBLIC from
    the legacy `_host`.
  - [ ] 7f. `preferred_plane=OVERLAY` with empty overlay emits one WARNING.
    Deferred to vpn-coordinator-coupling work (requires landscape
    construction harness).
- [x] 8. Property tests (`hypothesis`):
  - [x] 8a. `test_resolve_returns_address_or_none` (covered by
    `test_address_for_is_total` + `test_resolve_is_total_and_deterministic`).
  - [x] 8b. `test_resolve_is_deterministic`.
  - [x] 8c. `test_resolve_preferred_present` (via
    `test_preferred_address_first_present`).
  - [x] 8d. `test_resolve_fallback_walks_in_order` (via
    `test_preferred_address_first_present`).
  - [x] 8e. `test_resolve_total` — no exception path.
  - [x] 8f. `test_set_then_get_round_trip` (via
    `test_with_address_round_trip`).
- [x] 9. Add `hypothesis` to test dependencies if not already present.
- [x] 10. Update consumer specs (`ssh-address-plane-awareness`,
  `overlay-dns-resolver`) cross-links if the resolver method signature
  shifts from the published shape. No cross-link update required: the
  resolver signature shipped as the published shape
  (`resolve(*, plane, fallback_planes=None)` — task 3d) and did not
  shift, so the consumer-spec cross-links remain accurate.
