"""Tests for the :class:`FriendlyIdentifier` class."""

import re

from ccai.testbase import verification

from ccai.errors.exceptions import SemanticError
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_with_full_identifier_and_hint_only() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    verification.assert_equal(fid.full_identifier, "device-001-full")
    verification.assert_equal(fid.hint, "dev01")
    return


def test_construct_with_string_identity_match_compiles_pattern() -> None:
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=r"device-(\d+)-full",
    )

    compiled_pattern = fid._identity_match
    is_pattern = isinstance(compiled_pattern, re.Pattern)

    verification.assert_equal(is_pattern, True)
    verification.assert_equal(compiled_pattern.pattern, r"device-(\d+)-full")
    return


def test_construct_with_precompiled_identity_match_is_used_as_is() -> None:
    precompiled = re.compile(r"device-(\d+)-full")
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=precompiled,
    )

    stored_pattern = fid._identity_match

    is_same_object = stored_pattern is precompiled
    verification.assert_equal(is_same_object, True)
    return


def test_construct_with_non_matching_identity_match_raises_semantic_error() -> None:
    raised = False
    try:
        FriendlyIdentifier(
            full_identifier="device-001-full",
            hint="dev01",
            identity_match=r"router-(\d+)",
        )
    except SemanticError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


def test_full_identifier_property_returns_constructed_value() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    full_identifier_value = fid.full_identifier

    verification.assert_equal(full_identifier_value, "device-001-full")
    return


def test_hint_property_returns_constructed_value() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    hint_value = fid.hint

    verification.assert_equal(hint_value, "dev01")
    return


def test_identity_with_no_match_and_hint_returns_hint() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    identity_value = fid.identity

    verification.assert_equal(identity_value, "dev01")
    return


def test_identity_with_no_match_and_no_hint_returns_full_identifier() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint=None)

    identity_value = fid.identity

    verification.assert_equal(identity_value, "device-001-full")
    return


def test_identity_with_match_returns_first_capture_group() -> None:
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=r"device-(\d+)-full",
    )

    identity_value = fid.identity

    verification.assert_equal(identity_value, "001")
    return


def test_identity_with_match_returns_capture_group_from_precompiled_pattern() -> None:
    precompiled = re.compile(r"device-(\d+)-full")
    fid = FriendlyIdentifier(
        full_identifier="device-042-full",
        hint="dev42",
        identity_match=precompiled,
    )

    identity_value = fid.identity

    verification.assert_equal(identity_value, "042")
    return


def test_identity_after_update_to_incompatible_full_identifier_raises_semantic_error() -> None:
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=r"device-(\d+)-full",
    )

    fid.update_full_identifier(full_identifer="something-completely-different")

    raised = False
    try:
        _ = fid.identity
    except SemanticError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_identity_with_match_having_no_capture_group_raises_semantic_error() -> None:
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=r"device-\d+-full",
    )

    raised = False
    try:
        _ = fid.identity
    except SemanticError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# __eq__ regression tests (locks in the recently-fixed bugs)
# ---------------------------------------------------------------------------


def test_eq_two_identifiers_with_same_full_identifier_are_equal() -> None:
    left = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")
    right = FriendlyIdentifier(full_identifier="device-001-full", hint="alias")

    are_equal = (left == right)

    verification.assert_equal(are_equal, True)
    return


def test_eq_two_identifiers_with_different_full_identifiers_are_not_equal() -> None:
    left = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")
    right = FriendlyIdentifier(full_identifier="device-002-full", hint="dev01")

    are_equal = (left == right)

    verification.assert_equal(are_equal, False)
    return


def test_eq_with_string_substring_compares_equal() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    are_equal = (fid == "001")

    verification.assert_equal(are_equal, True)
    return


def test_eq_with_string_non_substring_does_not_compare_equal() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    are_equal = (fid == "router")

    verification.assert_equal(are_equal, False)
    return


def test_eq_with_none_returns_false_without_raising() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    raised = False
    are_equal = None
    try:
        are_equal = (fid == None)
    except Exception:
        raised = True

    verification.assert_equal(raised, False)
    verification.assert_equal(are_equal, False)
    return


def test_eq_with_int_returns_false_without_raising() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    raised = False
    are_equal = None
    try:
        are_equal = (fid == 42)
    except Exception:
        raised = True

    verification.assert_equal(raised, False)
    verification.assert_equal(are_equal, False)
    return


def test_eq_not_equal_uses_inverse_of_eq_for_friendly_identifier() -> None:
    left = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")
    right = FriendlyIdentifier(full_identifier="device-002-full", hint="dev01")

    not_equal_result = (left != right)

    verification.assert_equal(not_equal_result, True)
    return


# ---------------------------------------------------------------------------
# match()
# ---------------------------------------------------------------------------


def test_match_returns_true_when_hint_contains_stored_hint_and_is_substring_of_full() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="01")

    match_result = fid.match(hint="device-001")

    verification.assert_equal(match_result, True)
    return


def test_match_returns_false_when_hint_is_not_substring_of_full_identifier() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="01")

    match_result = fid.match(hint="router-01")

    verification.assert_equal(match_result, False)
    return


def test_match_returns_false_when_stored_hint_is_not_substring_of_argument() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="999")

    match_result = fid.match(hint="device-001")

    verification.assert_equal(match_result, False)
    return


def test_match_with_empty_hint_argument_returns_false() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="01")

    # The empty hint is a substring of full_identifier (find returns 0),
    # but the stored hint "01" is NOT a substring of the empty string.
    match_result = fid.match(hint="")

    verification.assert_equal(match_result, False)
    return


# ---------------------------------------------------------------------------
# relationship() and __str__()
# ---------------------------------------------------------------------------


def test_relationship_returns_documented_format() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    relationship_value = fid.relationship()

    verification.assert_equal(relationship_value, "dev01 -> device-001-full")
    return


def test_str_with_no_match_returns_hint() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    str_value = str(fid)

    verification.assert_equal(str_value, "dev01")
    return


def test_str_with_match_returns_capture_group() -> None:
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=r"device-(\d+)-full",
    )

    str_value = str(fid)

    verification.assert_equal(str_value, "001")
    return


# ---------------------------------------------------------------------------
# update_full_identifier
# ---------------------------------------------------------------------------


def test_update_full_identifier_changes_stored_value() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    fid.update_full_identifier(full_identifer="device-002-full")
    updated_value = fid.full_identifier

    verification.assert_equal(updated_value, "device-002-full")
    return


def test_update_full_identifier_with_no_match_does_not_raise() -> None:
    fid = FriendlyIdentifier(full_identifier="device-001-full", hint="dev01")

    raised = False
    try:
        fid.update_full_identifier(full_identifer="something-completely-different")
        # Identity should still resolve through the hint fallback.
        _ = fid.identity
    except Exception:
        raised = True

    verification.assert_equal(raised, False)
    return


def test_update_full_identifier_does_not_revalidate_against_match() -> None:
    """
        Documents the known design quirk: ``update_full_identifier`` does NOT
        re-validate against ``identity_match``.  The mismatch only surfaces
        later when ``identity`` is read.
    """
    fid = FriendlyIdentifier(
        full_identifier="device-001-full",
        hint="dev01",
        identity_match=r"device-(\d+)-full",
    )

    raised_on_update = False
    try:
        fid.update_full_identifier(full_identifer="something-completely-different")
    except Exception:
        raised_on_update = True

    verification.assert_equal(raised_on_update, False)
    verification.assert_equal(fid.full_identifier, "something-completely-different")
    return
