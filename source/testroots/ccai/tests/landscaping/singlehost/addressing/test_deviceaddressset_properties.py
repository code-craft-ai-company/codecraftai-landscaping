"""
    .. module:: test_deviceaddressset_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hypothesis property tests for
                   :class:`DeviceAddressSet`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import unittest

from typing import Dict, List, Optional

from ccai import testbase

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.interfaces.addressplane import AddressPlane
from ccai.landscaping.addressing.deviceaddressset import DeviceAddressSet


_NON_EMPTY_ADDR = st.text(min_size=1, max_size=12).filter(lambda s: len(s.strip()) > 0)
_OPTIONAL_ADDR = st.one_of(st.none(), _NON_EMPTY_ADDR, st.just(""))
_PLANE = st.sampled_from(list(AddressPlane))


def _build_overlay(values: List[Optional[str]]) -> Dict[str, Optional[str]]:
    """
        Build an overlay map from a list of optional values keyed by
        positional provider names.

        :param values: Address values to map under synthetic provider
            keys.

        :returns: A dictionary keyed ``provider_0``, ``provider_1``, ...
    """
    rtnval: Dict[str, Optional[str]] = {}
    for idx, v in enumerate(values):
        key = "provider_{}".format(idx)
        rtnval[key] = v
    return rtnval


# Module-level on purpose: the testbase sequencer collects module-level
# ``test_*`` and drives ``@given`` from the metadata the decorator records.
# A @given-decorated TestCase *method* never receives its generated
# arguments, so it cannot run at all.


@given(public=_OPTIONAL_ADDR, private=_OPTIONAL_ADDR,
       overlay_values=st.lists(_OPTIONAL_ADDR, min_size=0, max_size=3),
       plane=_PLANE)
def test_address_for_is_total(public: Optional[str],
                              private: Optional[str],
                              overlay_values: List[Optional[str]],
                              plane: AddressPlane) -> None:
    """
        ``address_for`` is total: it returns ``Optional[str]``
        without raising for any input.
    """
    overlay_map = _build_overlay(overlay_values)
    addr_set = DeviceAddressSet(public=public, private=private,
                                overlay=overlay_map)

    result = addr_set.address_for(plane=plane)
    is_valid = result is None or isinstance(result, str)
    assert is_valid
    if isinstance(result, str):
        assert len(result) > 0

    return

@given(public=_OPTIONAL_ADDR, private=_OPTIONAL_ADDR,
       overlay_values=st.lists(_OPTIONAL_ADDR, min_size=0, max_size=3),
       plane=_PLANE)
def test_has_matches_address_for(public: Optional[str],
                                 private: Optional[str],
                                 overlay_values: List[Optional[str]],
                                 plane: AddressPlane) -> None:
    """
        ``has(plane)`` iff ``address_for(plane) is not None``.
    """
    overlay_map = _build_overlay(overlay_values)
    addr_set = DeviceAddressSet(public=public, private=private,
                                overlay=overlay_map)

    candidate = addr_set.address_for(plane=plane)
    expected = candidate is not None
    actual = addr_set.has(plane=plane)
    assert actual == expected

    return

@given(plane=_PLANE, address=_NON_EMPTY_ADDR)
def test_with_address_round_trip(plane: AddressPlane,
                                 address: str) -> None:
    """
        ``with_address(plane=p, address=a).address_for(plane=p) == a``.
    """
    original = DeviceAddressSet()
    updated = original.with_address(plane=plane, address=address)

    result = updated.address_for(plane=plane)
    assert result == address

    # And the original must remain unchanged.
    original_result = original.address_for(plane=plane)
    assert original_result is None

    return

@given(plane=_PLANE, address=_NON_EMPTY_ADDR)
def test_with_address_immutable(plane: AddressPlane,
                                address: str) -> None:
    """
        Any mutating operation returns a new instance and leaves
        the original unchanged.
    """
    original = DeviceAddressSet(public="orig_public")
    updated = original.with_address(plane=plane, address=address)

    assert updated is not original
    # Original public slot is untouched.
    assert original.public() == "orig_public"

    return

@given(public=_OPTIONAL_ADDR, private=_OPTIONAL_ADDR,
       overlay_values=st.lists(_OPTIONAL_ADDR, min_size=0, max_size=3),
       planes=st.lists(_PLANE, min_size=1, max_size=4))
def test_preferred_address_first_present(public: Optional[str],
                                         private: Optional[str],
                                         overlay_values: List[Optional[str]],
                                         planes: List[AddressPlane]) -> None:
    """
        ``preferred_address(planes=[...])`` returns the address of
        the first populated plane in the supplied order, or raises
        consistently when none are populated.
    """
    overlay_map = _build_overlay(overlay_values)
    addr_set = DeviceAddressSet(public=public, private=private,
                                overlay=overlay_map)

    expected_addr: Optional[str] = None
    for p in planes:
        candidate = addr_set.address_for(plane=p)
        if candidate is not None:
            expected_addr = candidate
            break

    if expected_addr is None:
        with testbase.raises(LookupError):
            _ = addr_set.preferred_address(planes=planes)
    else:
        result = addr_set.preferred_address(planes=planes)
        assert result == expected_addr

    return

@given(public=_OPTIONAL_ADDR, private=_OPTIONAL_ADDR,
       overlay_values=st.lists(_OPTIONAL_ADDR, min_size=0, max_size=3),
       plane=_PLANE,
       fallbacks=st.lists(_PLANE, min_size=0, max_size=3))
def test_resolve_is_total_and_deterministic(public: Optional[str],
                                            private: Optional[str],
                                            overlay_values: List[Optional[str]],
                                            plane: AddressPlane,
                                            fallbacks: List[AddressPlane]) -> None:
    """
        ``resolve`` returns ``Optional[str]`` without raising and
        returns the same value on repeated invocation with the
        same input.
    """
    overlay_map = _build_overlay(overlay_values)
    addr_set = DeviceAddressSet(public=public, private=private,
                                overlay=overlay_map)

    first = addr_set.resolve(plane=plane, fallback_planes=fallbacks)
    second = addr_set.resolve(plane=plane, fallback_planes=fallbacks)

    is_valid = first is None or isinstance(first, str)
    assert is_valid
    assert first == second

    return


if __name__ == "__main__":
    unittest.main()
