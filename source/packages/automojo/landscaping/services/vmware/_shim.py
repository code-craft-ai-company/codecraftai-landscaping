"""
    .. module:: _shim
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Helper that powers every backward-compatibility re-export shim
               under ``automojo.landscaping.services.vmware``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    Each legacy module under ``services/vmware`` was extracted into the
    ``automojo-restclient-vsphere`` (or ``automojo-interop-vmworkstation``) package
    during M5. The legacy import paths are preserved for one release cycle by
    thin shim modules that delegate to :func:`install_shim`. The helper:

    * Re-exports the requested public symbols from the new module under the
      caller's module namespace so existing ``from <old> import <Name>`` calls
      keep resolving.
    * Emits exactly one :class:`DeprecationWarning` per process per old import
      path, so consumers see a clear migration nudge without log noise.

    Both the shim files and this helper are scheduled for deletion in M13.
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import sys
import warnings

from typing import Dict, List, Optional, Set


_WARNED: Set[str] = set()


def install_shim(*, old_path: str, new_module_name: str, public_names: List[str], aliases: Optional[Dict[str, str]] = None) -> None:
    """
        Wire a legacy shim module to its new home and emit a one-shot
        :class:`DeprecationWarning`.

        :param old_path: Dotted module path being deprecated (typically
                         ``__name__`` of the calling shim module).
        :param new_module_name: Dotted path of the replacement module that owns
                                the symbols going forward.
        :param public_names: Names to re-export onto the shim module. Each name
                             must resolve on the new module unless an alias is
                             supplied via ``aliases``.
        :param aliases: Optional mapping of legacy-name -> new-name. When a
                        legacy name has been renamed in the new package, list
                        the legacy name in ``public_names`` and add a
                        ``{"LegacyName": "NewName"}`` entry here so the shim
                        re-exports the new class under the legacy alias.

        :returns: None
    """
    if old_path not in _WARNED:
        _WARNED.add(old_path)
        msg_lines = [
            "{} is deprecated; import from {} instead.".format(old_path, new_module_name),
            "This shim will be removed in the next release.",
        ]
        msg = " ".join(msg_lines)
        warnings.warn(msg, DeprecationWarning, stacklevel=3)

    alias_map: Dict[str, str] = {}
    if aliases is not None:
        alias_map = aliases

    caller_module = sys.modules[old_path]
    new_module = __import__(new_module_name, fromlist=public_names)

    for legacy_name in public_names:
        source_name = legacy_name
        if legacy_name in alias_map:
            source_name = alias_map[legacy_name]
        symbol = getattr(new_module, source_name)
        setattr(caller_module, legacy_name, symbol)

    return None
