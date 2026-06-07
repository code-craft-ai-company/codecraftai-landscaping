"""
    .. module:: deviceaddressset
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the :class:`DeviceAddressSet` class
                   which is the canonical multi-plane address container
                   used by :class:`LandscapeDevice` and its consumers.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Dict, Iterable, List, Optional

from ccai.interfaces.addressplane import AddressPlane, IDeviceAddressSet


class DeviceAddressSet:
    """
        Canonical multi-plane address container for a landscape device.

        Implements the :class:`IDeviceAddressSet` protocol from
        ``codecraftai-interfaces`` and adds the richer setters, overlay
        provider map, and immutable ``with_address`` / ``preferred_address``
        helpers used by the landscape package itself.

        The set stores at most one address per plane for ``PUBLIC`` and
        ``PRIVATE`` and a provider-keyed dictionary for ``OVERLAY``. Empty
        strings are accepted by the setters (for YAML round-trip
        compatibility) and are filtered to ``None`` by every accessor.
    """

    def __init__(self, *, public: Optional[str] = None,
                 private: Optional[str] = None,
                 overlay: Optional[Dict[str, Optional[str]]] = None) -> None:
        """
            Constructs a new :class:`DeviceAddressSet`.

            :param public: The initial public-plane address, or ``None``.
            :param private: The initial private-plane address, or ``None``.
            :param overlay: A mapping of overlay-provider name to address.
                Pass ``None`` to start with no overlay providers.
        """
        self._public: Optional[str] = public
        self._private: Optional[str] = private
        if overlay is not None:
            self._overlay: Dict[str, Optional[str]] = dict(overlay)
        else:
            self._overlay = {}
        return

    @staticmethod
    def _filter_empty(value: Optional[str]) -> Optional[str]:
        """
            Apply the empty-string-is-absent rule to a stored value.

            :param value: The raw stored value.

            :returns: ``value`` when it is a non-empty string, else
                ``None``.
        """
        rtnval: Optional[str] = None
        if value is not None and len(value) > 0:
            rtnval = value
        return rtnval

    def public(self) -> Optional[str]:
        """
            Convenience accessor for the public-plane address.

            :returns: The public address, or ``None`` when not populated.
        """
        rtnval = self._filter_empty(self._public)
        return rtnval

    def private(self) -> Optional[str]:
        """
            Convenience accessor for the private-plane address.

            :returns: The private address, or ``None`` when not populated.
        """
        rtnval = self._filter_empty(self._private)
        return rtnval

    def overlay(self, *, provider: Optional[str] = None) -> Optional[str]:
        """
            Look up an overlay-plane address.

            :param provider: The overlay provider name. When ``None``,
                the first-inserted provider's address is returned.

            :returns: The overlay address, or ``None`` when not populated.
        """
        rtnval: Optional[str] = None

        if len(self._overlay) == 0:
            rtnval = None
        elif provider is None:
            first_key = next(iter(self._overlay))
            candidate = self._overlay[first_key]
            rtnval = self._filter_empty(candidate)
        elif provider in self._overlay:
            candidate = self._overlay[provider]
            rtnval = self._filter_empty(candidate)
        else:
            rtnval = None

        return rtnval

    def set_public(self, *, address: Optional[str]) -> None:
        """
            Set the public-plane address.

            :param address: The address to store. Empty strings are
                accepted and treated as absent by accessors.
        """
        self._public = address
        return

    def set_private(self, *, address: Optional[str]) -> None:
        """
            Set the private-plane address.

            :param address: The address to store. Empty strings are
                accepted and treated as absent by accessors.
        """
        self._private = address
        return

    def set_overlay(self, *, provider: str, address: Optional[str]) -> None:
        """
            Set the overlay-plane address for a given provider.

            :param provider: The overlay provider name (e.g. ``"tailscale"``).
            :param address: The address to store. Empty strings are
                accepted and treated as absent by accessors.
        """
        self._overlay[provider] = address
        return

    def address_for(self, *, plane: AddressPlane) -> Optional[str]:
        """
            Return the address for a given plane.

            :param plane: The plane whose address is requested.

            :returns: The address string when populated, otherwise
                ``None``.
        """
        rtnval: Optional[str] = None
        if plane == AddressPlane.PUBLIC:
            rtnval = self.public()
        elif plane == AddressPlane.PRIVATE:
            rtnval = self.private()
        elif plane == AddressPlane.OVERLAY:
            rtnval = self.overlay()
        else:
            rtnval = None
        return rtnval

    def has(self, *, plane: AddressPlane) -> bool:
        """
            Report whether a given plane is populated.

            :param plane: The plane to test.

            :returns: ``True`` when :meth:`address_for` would return a
                non-``None`` value for ``plane``, otherwise ``False``.
        """
        candidate = self.address_for(plane=plane)
        rtnval = candidate is not None
        return rtnval

    def planes(self) -> List[AddressPlane]:
        """
            Enumerate populated planes in ascending ordinal order.

            :returns: A list of populated :class:`AddressPlane` values in
                ascending ``IntEnum`` order.
        """
        ordered = (AddressPlane.PUBLIC, AddressPlane.PRIVATE, AddressPlane.OVERLAY)
        populated: List[AddressPlane] = []
        for plane in ordered:
            if self.has(plane=plane):
                populated.append(plane)
        return populated

    def present_planes(self) -> List[AddressPlane]:
        """
            Alias for :meth:`planes` retained for symmetry with
            documented landscape-side API names.

            :returns: A list of populated :class:`AddressPlane` values
                in ascending ``IntEnum`` order.
        """
        rtnval = self.planes()
        return rtnval

    def resolve(self, *, plane: AddressPlane,
                fallback_planes: Optional[List[AddressPlane]] = None) -> Optional[str]:
        """
            Resolve to a concrete address using a preferred plane and an
            ordered fallback list.

            :param plane: The preferred plane to try first.
            :param fallback_planes: An ordered list of planes to try
                when ``plane`` is absent. ``None`` means no fallback.

            :returns: The first non-empty address found by walking
                ``[plane] + fallback_planes``, or ``None`` when no
                attempted plane is populated.
        """
        attempted: List[AddressPlane] = [plane]
        if fallback_planes is not None:
            for fp in fallback_planes:
                attempted.append(fp)

        rtnval: Optional[str] = None
        for candidate_plane in attempted:
            candidate = self.address_for(plane=candidate_plane)
            if candidate is not None:
                rtnval = candidate
                break

        return rtnval

    def with_address(self, *, plane: AddressPlane,
                     address: Optional[str],
                     provider: Optional[str] = None) -> "DeviceAddressSet":
        """
            Return a new :class:`DeviceAddressSet` with ``plane`` set to
            ``address``. The original instance is not modified.

            :param plane: The plane to populate in the returned set.
            :param address: The address to store for ``plane``.
            :param provider: When ``plane`` is :attr:`AddressPlane.OVERLAY`,
                the overlay provider name. Defaults to ``"default"``
                when omitted.

            :returns: A new :class:`DeviceAddressSet` carrying the
                requested mutation.
        """
        new_public = self._public
        new_private = self._private
        new_overlay: Dict[str, Optional[str]] = dict(self._overlay)

        if plane == AddressPlane.PUBLIC:
            new_public = address
        elif plane == AddressPlane.PRIVATE:
            new_private = address
        elif plane == AddressPlane.OVERLAY:
            overlay_provider = provider
            if overlay_provider is None:
                overlay_provider = "default"
            new_overlay[overlay_provider] = address

        rtnval = DeviceAddressSet(public=new_public, private=new_private,
                                  overlay=new_overlay)
        return rtnval

    def preferred_address(self, *, planes: Iterable[AddressPlane]) -> str:
        """
            Return the address of the first populated plane in
            ``planes``, in the order supplied.

            :param planes: An iterable of planes to try in priority
                order.

            :returns: The first populated address.
            :raises: :class:`LookupError` when no plane in ``planes``
                is populated.
        """
        attempted: List[AddressPlane] = list(planes)

        rtnval: Optional[str] = None
        for candidate_plane in attempted:
            candidate = self.address_for(plane=candidate_plane)
            if candidate is not None:
                rtnval = candidate
                break

        if rtnval is None:
            err_msg_lines = ["No populated plane found in requested set."]
            err_msg_lines.append("REQUESTED:")
            for p in attempted:
                err_msg_lines.append("    {}".format(p.name))
            err_msg_lines.append("POPULATED:")
            for p in self.planes():
                err_msg_lines.append("    {}".format(p.name))
            err_msg = "\n".join(err_msg_lines)
            raise LookupError(err_msg)

        return rtnval

    def __repr__(self) -> str:
        """
            Returns a concise string representation for debugging.

            :returns: A repr string showing populated planes.
        """
        parts = []
        if self.public() is not None:
            parts.append("public={}".format(self.public()))
        if self.private() is not None:
            parts.append("private={}".format(self.private()))
        if len(self._overlay) > 0:
            parts.append("overlay={}".format(dict(self._overlay)))
        body = ", ".join(parts)
        rtnval = "<DeviceAddressSet {}>".format(body)
        return rtnval


# Runtime assertion: the concrete class must satisfy the protocol.
_proto_check: IDeviceAddressSet = DeviceAddressSet()


__all__ = ["DeviceAddressSet"]
