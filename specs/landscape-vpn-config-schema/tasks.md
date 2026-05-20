# Implementation Plan — Landscape VPN Config Schema

- [x] 1. Create `automojo/landscaping/config/__init__.py` (if not present).
- [x] 2. Create `config/vpnproviderentry.py` with the `VPNProviderEntry`
  dataclass.
- [x] 3. Create `config/landscapeconfigdiagnostic.py` with the
  `LandscapeConfigDiagnostic` dataclass and the
  `LandscapeConfigError` exception.
- [x] 4. Create `config/vpnconfigschema.py`:
  - [x] 4a. Constants for accepted `kind` values and accepted
    `default_plane` values.
  - [x] 4b. `validate_landscape_vpn_block(*, doc) ->
    List[LandscapeConfigDiagnostic]`.
  - [x] 4c. `parse_landscape_vpn_block(*, doc) ->
    Tuple[AddressPlane, List[VPNProviderEntry]]` returning the canonical
    parse result on success and raising `LandscapeConfigError` on any
    error-severity diagnostic.
- [x] 5. Wire the loader:
  - [x] 5a. Call the validator from the existing landscape loader.
  - [x] 5b. On any error diagnostic, raise `LandscapeConfigError`.
  - [x] 5c. Log each warning diagnostic once with the file path attached.
- [x] 6. Extend `LandscapeRoot` to hold `vpn_providers: List[VPNProviderEntry]`
  and `default_plane: AddressPlane`.
- [x] 7. Extend `LandscapeDevice` to hold `vpn_provider: Optional[str]`,
  `vpn_managed: bool`, `vpn_advertise_tags: List[str]` (initialised in
  `__init__` per coding standards).
- [x] 8. Plane resolution at device construction:
  device-level `preferred_plane` wins; else root `default_plane`; else
  `PUBLIC`.
- [x] 9. Apply project coding standards (named-only, explicit returns).
- [x] 10. Tests — example-based:
  - [x] 10a. `test_no_vpn_block_returns_empty_diagnostics`.
  - [x] 10b. `test_tailscale_only_parses_one_provider`.
  - [x] 10c. `test_per_device_override_sets_preferred_plane`.
  - [x] 10d. `test_invalid_kind_raises_LandscapeConfigError`.
  - [x] 10e. `test_unknown_key_emits_warning_not_error`.
  - [x] 10f. `test_device_references_unknown_provider_errors`.
  - [x] 10g. `test_default_plane_resolution_precedence`.
- [x] 11. Fixture files: four landscape YAMLs as listed in the design.
- [x] 12. Regression test that every existing landscape fixture in the
  package produces zero new diagnostics.
- [x] 13. Cross-link with `automojo-configuration` `vpn-config-schema` spec
  so the schema fragment definitions stay in sync.
