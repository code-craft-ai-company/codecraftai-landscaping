"""
    .. module:: vpnproviderentry
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the :class:`VPNProviderEntry`
                   dataclass used by the landscape-level VPN schema.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class VPNProviderEntry:
    """
        Typed representation of a single ``vpn.providers[*]`` entry in
        ``landscape.yaml``.

        This is the landscape-layer projection of the upstream
        :class:`ccai.configuration.schemas.vpnconfigschema.VPNOverlayProfile`
        that preserves landscape-specific field names (``tailnet``,
        ``network_slug``, ``default_tags``) called for by the
        ``landscape-vpn-config-schema`` spec.

        :param name: The landscape-unique name a device's ``vpn.provider``
            override references.
        :param kind: The VPN kind string. Currently one of
            ``"tailscale"`` or ``"twingate"``.
        :param credential_ref: The identifier resolved through
            :class:`ccai.credentials.credentialmanager.CredentialManager`.
        :param tailnet: Tailnet name when ``kind == "tailscale"``;
            otherwise ``None``.
        :param network_slug: Network slug when ``kind == "twingate"``;
            otherwise ``None``.
        :param default_tags: Default tag list advertised by devices that
            do not override them.
    """
    name: str
    kind: str
    credential_ref: str
    tailnet: Optional[str] = None
    network_slug: Optional[str] = None
    default_tags: List[str] = field(default_factory=list)
