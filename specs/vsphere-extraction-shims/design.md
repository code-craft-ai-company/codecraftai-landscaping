# Design

## Overview

This feature populates `automojo-landscaping/source/packages/automojo/landscaping/services/vmware/`
with thin shim modules that re-export the matching symbols from
`automojo-interop-vsphere` (and `automojo-interop-vmworkstation` for the
VMware Workstation agent) and emit a `DeprecationWarning` exactly once per
process per import path. The shims exist for a single release cycle and are
removed under the M13 milestone.

Each shim is generated from a single helper (`_shim.install_shim`) so the
text of the warning, the once-per-process suppression set, and the
`stacklevel` handling are uniform. No new public API is introduced.

The landscape-side glue (`vspherecoordinator.py`, `vsphereservice.py`,
`vspherecoordinatorcoupling.py`) stays in this package — it is not extracted
and not shimmed; it simply updates its imports to point at the new package.

**See Also:**
- Master plan §6.2 (VSphere extraction)
- automojo-interop-vsphere `vsphere-client-rest-base` spec
- automojo-interop-vsphere `vsphere-apigroups-migration` spec
- automojo-interop-vmworkstation `vmworkstation-client` spec

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│   Downstream consumer (still using old import path)          │
│   from automojo.landscaping.services.vmware.vsphere          │
│                  .vsphereagent import VSphereAgent           │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│   Shim module (~5 lines)                                     │
│   automojo/landscaping/services/vmware/vsphere/vsphereagent  │
│                                                              │
│   _shim.install_shim(                                        │
│       old_path="automojo.landscaping.services.vmware."       │
│                "vsphere.vsphereagent",                       │
│       new_module_name="automojo.interop.vsphere"             │
│                       ".vsphereclient",                      │
│       public_names=["VSphereAgent"],                         │
│   )                                                          │
│   from automojo.interop.vsphere.vsphereclient import *       │
└──────────────────────────────┬───────────────────────────────┘
                               │ DeprecationWarning (once per process)
                               ▼
                  warnings.warn(..., stacklevel=2)
```

---

## Module Layout

```
source/packages/automojo/landscaping/services/vmware/
├── _shim.py                       ← install_shim() helper
├── DEPRECATIONS.md                ← per-shim removal schedule
├── vsphere/
│   ├── vsphereagent.py            (shim)
│   ├── vsphereservice.py          (unchanged — not extracted)
│   ├── vspherecoordinator.py      (unchanged — imports updated)
│   ├── vspherecoordinatorcoupling.py (unchanged — imports updated)
│   └── ext/
│       ├── certificatemanagementext.py (shim)
│       ├── clusterext.py               (shim)
│       └── ...                          (shim — one per ext module)
├── datastructures/
│   ├── model/  (one shim per moved DTO)
│   └── specs/  (one shim per moved spec)
├── metasphere/  (one shim per moved enum)
└── vmworkstationagent.py          (shim → automojo-interop-vmworkstation)
```

Tests:

```
source/testroots/.../landscaping/services/vmware/
├── test_shims_reexport.py
├── test_shim_warns_once.py
└── test_install_shim_helper.py
```

---

## `install_shim` Helper

```python
# _shim.py
import sys
import warnings
from typing import List

_WARNED: set = set()

def install_shim(
    *,
    old_path: str,
    new_module_name: str,
    public_names: List[str],
) -> None:
    """Re-export public_names from new_module_name into the calling
    module, and emit a one-shot DeprecationWarning.

    :param old_path: Dotted module path being deprecated.
    :param new_module_name: Dotted path of the replacement module.
    :param public_names: Names to re-export.

    :returns: None
    """
    if old_path not in _WARNED:
        _WARNED.add(old_path)
        msg = (
            "{} is deprecated; import from {} instead. "
            "This shim will be removed in the next release."
        ).format(old_path, new_module_name)
        warnings.warn(msg, DeprecationWarning, stacklevel=3)

    caller_module = sys.modules[old_path]
    new_module = __import__(new_module_name, fromlist=public_names)
    for name in public_names:
        setattr(caller_module, name, getattr(new_module, name))

    return None
```

Each shim file is then ~5 lines:

```python
from automojo.landscaping.services.vmware._shim import install_shim
install_shim(
    old_path=__name__,
    new_module_name="automojo.interop.vsphere.vsphereclient",
    public_names=["VSphereAgent"],
)
```

---

## Warning Cardinality

The `_WARNED` set is module-level in `_shim.py`. Each shim path appears at
most once across the process. Re-importing the shim (e.g., via
`importlib.reload`) intentionally does not re-warn — this preserves quiet
test runs that probe both old and new import paths in the same process.

---

## Removal Schedule

`DEPRECATIONS.md` lists each shim with the release in which it will be
removed (one release after this feature ships). The M13 milestone in the
implementation plan removes the shim files; the helper `_shim.py` is also
removed at that time.

---

## Testing Strategy

- `test_install_shim_helper.py`:
  - Calling `install_shim` once attaches the named symbols to the caller
    module and emits one `DeprecationWarning`.
  - Calling `install_shim` again with the same `old_path` emits no further
    warning.
- `test_shims_reexport.py`:
  - For each shim module, import the deprecated path and assert the
    re-exported symbol `is` identity-equal to the one imported directly
    from the new module.
- `test_shim_warns_once.py`:
  - Use `warnings.catch_warnings(record=True)` to import the same shim from
    two distinct test-side import sites; assert exactly one
    `DeprecationWarning` was recorded.
- No test requires `automojo-interop-vsphere` to be fully implemented — a
  stub package can be installed in the test environment to satisfy the
  imports during M5.
