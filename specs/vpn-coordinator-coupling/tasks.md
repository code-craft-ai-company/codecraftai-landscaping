# Implementation Plan — VPN Coordinator Coupling

- [x] 1. Create `automojo/landscaping/coupling/__init__.py` (if not present).
- [x] 2. Create `coupling/vpncouplingresult.py` with `VPNCouplingResult`
  dataclass.
- [x] 3. Create `coupling/exceptions.py` with
  `VPNCoordinatorAmbiguousMatchError`.
- [x] 4. Create `coupling/aspectslandscapecoupling.py` with
  `AspectsLandscapeCoupling` and `DEFAULT_LANDSCAPE_COUPLING_ASPECTS`.
- [x] 5. Create `coupling/vpncoordinatorcoupling.py`:
  - [x] 5a. `__init__(*, provider, credential, control_plane, vpn_managed=False)`.
  - [x] 5b. `couple(*, devices, aspects=DEFAULT_LANDSCAPE_COUPLING_ASPECTS)
    -> VPNCouplingResult`.
  - [x] 5c. `refresh(*, devices, aspects=...) -> VPNCouplingResult` — alias
    that recomputes the control-plane index.
  - [x] 5d. `decouple(*, devices, aspects=...) -> None`.
  - [x] 5e. Match algorithm per design (hostname → tag → unmatched).
  - [x] 5f. Idempotency: only call `set_overlay` when address differs.
  - [x] 5g. Managed-host path: construct an `IVPNClient` and register on the
    device.
- [ ] 6. Update `LandscapeDevice` to expose `vpn_client_for(provider) ->
  Optional[IVPNClient]` and to hold the registry.
- [x] 7. Apply project coding standards (named-only, explicit returns).
- [x] 8. Tests — example-based:
  - [x] 8a. `test_couple_hostname_match_attaches_overlay`.
  - [x] 8b. `test_couple_tag_match_attaches_overlay`.
  - [x] 8c. `test_couple_tag_match_multiple_raises_when_strict`.
  - [x] 8d. `test_couple_tag_match_multiple_records_when_lenient`.
  - [x] 8e. `test_couple_hostname_supersedes_tag`.
  - [x] 8f. `test_couple_unmatched_leaves_overlay_untouched`.
  - [x] 8g. `test_recouple_is_idempotent`.
  - [x] 8h. `test_decouple_clears_overlay_only`.
  - [x] 8i. `test_managed_host_without_credential_raises`.
  - [x] 8j. `test_managed_host_registers_vpn_client`.
- [ ] 9. Fixture files: control-plane device list, landscape YAML snippet.
- [ ] 10. Register the coupling kind with the landscape coordinator factory
  so YAML-declared `vpn:` blocks construct it automatically (cross-spec with
  `landscape-vpn-config-schema`).
