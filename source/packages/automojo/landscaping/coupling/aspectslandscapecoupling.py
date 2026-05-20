"""
    .. module:: aspectslandscapecoupling
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the :class:`AspectsLandscapeCoupling`
                   carrier and the default singleton used by the landscape
                   coupling verbs (``couple``, ``refresh``, ``decouple``).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass


@dataclass
class AspectsLandscapeCoupling:
    """
        Behaviour-modifying parameters carried into the landscape
        coupling verbs.

        :param refresh_interval_seconds: Suggested interval between
            background ``refresh`` invocations for callers that drive a
            refresh loop. The coupling itself does not poll; this value
            is metadata for the caller.
        :param timeout_seconds: Per-call timeout that callers may apply
            when invoking the coupling.
        :param raise_on_ambiguous: When ``True`` (the default), a tag
            match that resolves to more than one VPN device record
            raises :class:`VPNCoordinatorAmbiguousMatchError`. When
            ``False``, the ambiguous match is recorded on the returned
            :class:`VPNCouplingResult` and the device is left unmatched.
    """
    refresh_interval_seconds: float = 30.0
    timeout_seconds: float = 60.0
    raise_on_ambiguous: bool = True


DEFAULT_LANDSCAPE_COUPLING_ASPECTS = AspectsLandscapeCoupling()


__all__ = ["AspectsLandscapeCoupling", "DEFAULT_LANDSCAPE_COUPLING_ASPECTS"]
