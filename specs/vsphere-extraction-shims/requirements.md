# Requirements

## Introduction

The `vsphere-extraction-shims` feature provides one-release-cycle backward
compatibility for downstream consumers of the vsphere-related code that is
moving out of `automojo-landscaping/services/vmware/` into the new
`automojo-interop-vsphere` package. Each shim module lives at the old import
path, re-exports the same names from the new package, and emits a
`DeprecationWarning` exactly once per process per import path.

The shims are explicitly scoped to a single release cycle. After that, the
shim files are deleted as part of the M13 cleanup milestone.

All shim modules are pure import-and-warn — no logic, no behaviour. The
warning emission count is bounded so the warning appears once per import even
when the shim is imported from many call sites.

---

## Requirements

### Requirement 1: Re-Export From New Package

**User Story:** As a downstream consumer, I want my existing import statements
to keep working unchanged for one release cycle while I migrate.

#### Acceptance Criteria

1. THE SYSTEM SHALL provide a shim module at every old import path that
   downstream code used:
   - `automojo.landscaping.services.vmware.vsphere.vsphereagent`
   - `automojo.landscaping.services.vmware.vsphere.ext.<each ext module>`
   - `automojo.landscaping.services.vmware.datastructures.model.<each model>`
   - `automojo.landscaping.services.vmware.datastructures.specs.<each spec>`
   - `automojo.landscaping.services.vmware.metasphere.<each enum>`
   - `automojo.landscaping.services.vmware.vmworkstationagent`
2. WHEN a shim module is imported THE SYSTEM SHALL re-export every public
   symbol the old module exported, sourced from the matching module in
   `automojo-interop-vsphere` (or `automojo-interop-vmworkstation`).
3. THE SYSTEM SHALL preserve original symbol names — no renaming.

### Requirement 2: Emit `DeprecationWarning` Exactly Once Per Import

**User Story:** As a downstream maintainer, I want a clear, single warning per
deprecated module so log noise stays low while migration is visible.

#### Acceptance Criteria

1. WHEN a shim module is first imported in a process THE SYSTEM SHALL emit
   a `DeprecationWarning` with:
   - Old import path.
   - New import path.
   - A pointer to the migration guide / spec.
2. THE SYSTEM SHALL emit the warning at most ONCE per process per module
   path, even when the module is imported from many call sites.
3. THE SYSTEM SHALL set `stacklevel=2` on the warning so the caller's file
   appears as the warning source.
4. THE SYSTEM SHALL use `warnings.warn(...)`; no logger usage. Consumers
   filter / suppress through standard `warnings` machinery.

### Requirement 3: No New Surface Area

**User Story:** As a maintainer of the `automojo-interop-vsphere` package, I
want the shims to add nothing — no helper classes, no extra documentation —
so deletion is trivial.

#### Acceptance Criteria

1. THE SYSTEM SHALL NOT introduce any new public class, function, or
   constant inside a shim module beyond the re-export and the warning call.
2. THE SYSTEM SHALL NOT introduce any new dependency in
   `automojo-landscaping`.

### Requirement 4: Shim Module Construction Is Generated, Not Hand-Authored

**User Story:** As an author of this feature, I want every shim to come from
one template so the warning text, structure, and once-per-process logic are
identical across all ~50 shim files.

#### Acceptance Criteria

1. THE SYSTEM SHALL include a single `_shim.py` helper that exports a
   `install_shim(*, old_path, new_module_name, public_names)` function used
   by every shim module.
2. THE SYSTEM SHALL keep each shim module under 10 lines (the call into
   `install_shim` plus the `from new_module import *` line).

### Requirement 5: Deletion Path Is Documented

**User Story:** As a release manager, I want a clear list of what to delete
when the deprecation window closes.

#### Acceptance Criteria

1. THE SYSTEM SHALL include a `DEPRECATIONS.md` (or a section in the
   package Agents.md) listing every shim module and the release in which it
   will be removed.
2. THE SYSTEM SHALL set the deletion target to one release after the shim
   first lands.

### Requirement 6: Tests Cover Re-Export and Warning Cardinality

#### Acceptance Criteria

1. THE SYSTEM SHALL include a test for every shim asserting:
   - The expected public names are importable from the old path.
   - The imported symbol is identity-equal to the one from the new package.
2. THE SYSTEM SHALL include a test asserting that importing the same shim
   twice in the same process produces exactly one `DeprecationWarning`
   (use `warnings.catch_warnings(record=True)` to count).
