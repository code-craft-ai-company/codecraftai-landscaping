"""
    .. module:: exceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing exception types raised by the
                   landscape coupling layer.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


class VPNCoordinatorAmbiguousMatchError(Exception):
    """
        Raised by :class:`VPNCoordinatorCoupling` when a landscape device's
        tag matches more than one VPN control-plane device record and the
        caller requested strict ambiguity handling.

        The exception message lists every candidate ``device_id`` so the
        operator can disambiguate by editing the landscape config (either
        adding a more specific tag or by switching the device to a
        hostname match).
    """
    pass


__all__ = ["VPNCoordinatorAmbiguousMatchError"]
