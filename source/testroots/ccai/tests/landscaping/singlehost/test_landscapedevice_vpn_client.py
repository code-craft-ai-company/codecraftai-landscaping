"""
    .. module:: test_landscapedevice_vpn_client
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for the :meth:`LandscapeDevice.vpn_client_for`
                   accessor and the :meth:`register_vpn_client`
                   companion that populate the per-device VPN client
                   registry.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from unittest.mock import MagicMock

from ccai.errors.exceptions import SemanticError
from ccai.interfaces.ivpnclient import IVPNClient

from ccai.landscaping.friendlyidentifier import FriendlyIdentifier
from ccai.landscaping.landscapedevice import LandscapeDevice


def _build_bare_device(*, full_id: str = "host-1.example.com",
                       hint: str = "host-1") -> LandscapeDevice:
    """
        Build a bare-bones :class:`LandscapeDevice` without going through
        the full ``__init__`` chain (which requires a Landscape).

        :param full_id: The device full identifier.
        :param hint: The friendly-identifier hint.

        :returns: A minimally-populated :class:`LandscapeDevice`.
    """
    dev = object.__new__(LandscapeDevice)
    dev._friendly_id = FriendlyIdentifier(full_identifier=full_id, hint=hint)
    dev._vpn_clients = {}
    return dev


def test_register_vpn_client_then_vpn_client_for_returns_client() -> None:
    """
        A client registered through :meth:`register_vpn_client` is
        returned by :meth:`vpn_client_for` for the same provider.
    """
    dev = _build_bare_device()
    fake_client = MagicMock(spec=IVPNClient)

    dev.register_vpn_client(provider="tailscale", client=fake_client)

    found = dev.vpn_client_for(provider="tailscale")
    assert found is fake_client
    return


def test_vpn_client_for_raises_when_provider_absent() -> None:
    """
        :meth:`vpn_client_for` raises :class:`SemanticError` when no
        client has been registered for the requested provider.
    """
    dev = _build_bare_device()

    raised = None
    try:
        _ = dev.vpn_client_for(provider="tailscale")
    except SemanticError as exc:
        raised = exc

    assert raised is not None
    return


def test_vpn_client_for_isolates_providers() -> None:
    """
        Clients registered under different providers are looked up
        independently and do not collide.
    """
    dev = _build_bare_device()
    tailscale_client = MagicMock(spec=IVPNClient)
    twingate_client = MagicMock(spec=IVPNClient)

    dev.register_vpn_client(provider="tailscale", client=tailscale_client)
    dev.register_vpn_client(provider="twingate", client=twingate_client)

    assert dev.vpn_client_for(provider="tailscale") is tailscale_client
    assert dev.vpn_client_for(provider="twingate") is twingate_client
    return


def test_register_vpn_client_replaces_prior_client() -> None:
    """
        A second registration for the same provider replaces the prior
        client.
    """
    dev = _build_bare_device()
    first_client = MagicMock(spec=IVPNClient)
    second_client = MagicMock(spec=IVPNClient)

    dev.register_vpn_client(provider="tailscale", client=first_client)
    dev.register_vpn_client(provider="tailscale", client=second_client)

    assert dev.vpn_client_for(provider="tailscale") is second_client
    return
