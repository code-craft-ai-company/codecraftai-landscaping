"""
    .. module:: landscapeconfigdiagnostic
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the
                   :class:`LandscapeConfigDiagnostic` dataclass and the
                   :class:`LandscapeConfigError` exception used by the
                   landscape configuration validators.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass
from typing import Optional


SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass(frozen=True)
class LandscapeConfigDiagnostic:
    """
        Structured diagnostic record produced by landscape configuration
        validators.

        Editor integrations and CLI commands (``arcli landscape validate``)
        can surface ``path``, ``line`` and ``column`` without re-parsing
        the source file.

        :param severity: Either ``"error"`` or ``"warning"``.
        :param path: Dotted/indexed path identifying the offending node
            (e.g. ``"vpn.providers[1].kind"``).
        :param message: Human-readable message describing the issue.
        :param line: Optional line number into the source document.
        :param column: Optional column number into the source document.
    """
    severity: str
    path: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None


class LandscapeConfigError(Exception):
    """
        Raised when a landscape configuration section contains a
        hard error that prevents the landscape from loading.
    """
    pass
