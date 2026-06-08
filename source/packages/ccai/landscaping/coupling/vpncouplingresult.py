"""
    .. module:: vpncouplingresult
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the :class:`VPNCouplingResult`
                   dataclass returned by
                   :meth:`VPNCoordinatorCoupling.couple` and
                   :meth:`VPNCoordinatorCoupling.refresh`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass, field
from typing import List


@dataclass
class VPNCouplingResult:
    """
        Result record returned by a single ``couple`` or ``refresh``
        invocation of :class:`VPNCoordinatorCoupling`.

        :param provider: The provider name the coupling acted under
            (for example ``"tailscale"`` or ``"twingate"``).
        :param updated: Number of devices whose overlay slot was mutated
            during this invocation.
        :param skipped: Number of devices skipped without mutation
            because the candidate address was ``None`` (Twingate
            asymmetry) or the existing slot already held the desired
            address (idempotent re-entry).
        :param unmatched: Number of devices for which no peer record
            could be found by hostname or by tag.
        :param ambiguous_tag_matches: Identifiers of devices whose tag
            match resolved to more than one peer record when the caller
            requested lenient ambiguity handling.
    """
    provider: str
    updated: int = 0
    skipped: int = 0
    unmatched: int = 0
    ambiguous_tag_matches: List[str] = field(default_factory=list)


__all__ = ["VPNCouplingResult"]
