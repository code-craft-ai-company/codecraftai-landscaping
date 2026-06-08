# Implementation Plan — VSphere Extraction Shims

- [x] 1. Create `ccai/landscaping/services/vmware/_shim.py` with the
  `install_shim(*, old_path, new_module_name, public_names)` helper and
  the module-level `_WARNED` set.
- [x] 2. Enumerate every public symbol that currently lives in
  `ccai/landscaping/services/vmware/vsphere/`, `ext/`,
  `datastructures/model/`, `datastructures/specs/`, `metasphere/`, and
  `vmworkstationagent.py`. Produce a CSV mapping
  `old_path,new_module_name,public_names`.
- [x] 3. For each row in the CSV, generate a shim module at the old path:
  - [x] 3a. `vsphere/vsphereagent.py` → `ccai.interop.vsphere.vsphereclient` (`VSphereAgent`).
  - [x] 3b. One shim per `ext/*ext.py` → matching `ccai.interop.vsphere.apigroups.*group`.
  - [x] 3c. One shim per `datastructures/model/*.py` → `ccai.interop.vsphere.model.*`.
  - [x] 3d. One shim per `datastructures/specs/*.py` → `ccai.interop.vsphere.specs.*`.
  - [x] 3e. One shim per `metasphere/*.py` → `ccai.interop.vsphere.enums.*`.
  - [ ] 3f. `vmworkstationagent.py` → `ccai.interop.vmworkstation.vmworkstationclient`.
        (Deferred — Phase 3b owns the workstation move and will land its own shim.)
- [ ] 4. Update `vspherecoordinator.py`, `vsphereservice.py`,
  `vspherecoordinatorcoupling.py` to import from the new package directly
  (not via shims).
        (Deferred — current Phase 3c instructions explicitly keep those files
        importing via the legacy shim paths; the direct-import switch will land
        once VSphereClient's keyword-only constructor is wired into
        `VSphereService`.)
- [x] 5. Add `DEPRECATIONS.md` to `services/vmware/` listing every shim and
  the release in which it will be removed.
- [x] 6. Apply project coding standards (named-only params, explicit returns
  on helper functions).
- [x] 7. Tests:
  - [x] 7a. `test_install_shim_helper_emits_once`.
  - [x] 7b. `test_install_shim_helper_reexports_public_names`.
  - [x] 7c. For each shim, `test_<shim>_reexports_expected_symbols`.
  - [x] 7d. `test_shim_warns_only_once_per_process_per_path`.
- [x] 8. Stub `codecraftai-interop-vsphere` and
  `codecraftai-interop-vmworkstation` installation in the test environment
  so import resolution succeeds during M5 before the new packages are
  feature-complete.
- [ ] 9. Add a Markdown linter exception for `DEPRECATIONS.md` if any
  pre-commit hook flags it.
- [ ] 10. Schedule M13 follow-up: delete every shim file and the `_shim.py`
  helper (called out in `IMPLEMENTATION-PLAN.md`).
