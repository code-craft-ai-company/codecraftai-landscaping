"""
    .. module:: friendlyidentifier
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`FriendlyIdentifier` class which can
    be used to reference devices by a short name while allowing the landscaping
    modules to link or associate a full identifier with the short name.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import Optional, Union

import re

from ccai.errors.exceptions import SemanticError

class FriendlyIdentifier:
    """
        Associates a short identifier with a full identifier string and an
        optional identity match pattern.
    """

    def __init__(self, full_identifier: str, hint: str, identity_match: Optional[Union[re.Pattern, str]]=None):
        """
            Constructs a :class:`FriendlyIdentifier` instance.

            :param full_identifier: The full identifier string.
            :param hint: A short name used for quick reference.
            :param identity_match: Optional regular expression used to extract an identity value.
        """
        self._full_identifier = full_identifier
        self._hint = hint

        self._identity_match = identity_match
        if self._identity_match is not None and isinstance(identity_match, str):
            self._identity_match = re.compile(identity_match)

        # If a short_match expression is specified, it must have a match in the full identifier.
        if self._identity_match is not None:
            mobj = self._identity_match.match(self._full_identifier)
            if mobj is None:
                errmsg = "The specified identifier is not compatible with the short match expression provided."
                raise SemanticError(errmsg)
        return
    
    @property
    def full_identifier(self):
        """
            The full identifier used to reference something.
        """
        return self._full_identifier
    
    @property
    def hint(self):
        """
            A reduced name that represents a adequatly unique portion
            of the full identifier.  
        """
        return self._hint

    @property
    def identity(self):
        """
            Provides a short identifier for this instance.

            :returns: The resolved identity string for the identifier.

            :raises SemanticError: If a match expression is configured but the
                                   full identifier no longer matches it (typically
                                   because :meth:`update_full_identifier` was given
                                   an incompatible value), or if the match
                                   expression has no capturing group.
        """
        id = None

        if self._identity_match is not None:
            mobj = self._identity_match.match(self._full_identifier)
            if mobj is None:
                errmsg_lines = [
                    "Identity match expression no longer matches the current full identifier.",
                    "    FULL_IDENTIFIER: {}".format(self._full_identifier),
                    "    PATTERN: {}".format(self._identity_match.pattern),
                ]
                errmsg = "\n".join(errmsg_lines)
                raise SemanticError(errmsg)
            groups = mobj.groups()
            if len(groups) == 0:
                errmsg_lines = [
                    "Identity match expression has no capturing group.",
                    "    PATTERN: {}".format(self._identity_match.pattern),
                ]
                errmsg = "\n".join(errmsg_lines)
                raise SemanticError(errmsg)
            id = groups[0]
        elif self._hint is not None:
            id = self._hint
        else:
            id = self._full_identifier

        return id

    def match(self, hint:str) -> bool:
        """
            Indicates if the hint provided provides a match for this FriendlyIdentifier.
        """
        result = False
        if self._full_identifier.find(hint) > -1 and hint.find(self._hint) > -1:
            result = True
        return result

    def relationship(self) -> str:
        """
            Returns a string that describes the relationship between the hint and
            the full identifier.

            :returns: The formatted relationship string.
        """
        rel = self._hint + " -> " + self._full_identifier
        return rel

    def update_full_identifier(self, full_identifer: str):
        """
            Updates the stored full identifier with a new value.

            :param full_identifer: The new full identifier string.
        """
        self._full_identifier = full_identifer
        return

    def __eq__(self, other):
        """
            Compares two identifiers for equivalence.

            :param other: Another :class:`FriendlyIdentifier`, a string, or any
                          other value.  For strings, equality is true when the
                          string is a substring of the full identifier (matching
                          the existing behaviour).  For unrelated types, returns
                          ``NotImplemented`` so Python can fall back to the
                          other operand's ``__eq__``.

            :returns: ``True`` when the identifiers are equivalent, ``False``
                      when they are comparable but not equal, or
                      ``NotImplemented`` when ``other`` is of an unrelated type.
        """
        if isinstance(other, FriendlyIdentifier):
            result = self._full_identifier == other._full_identifier
        elif isinstance(other, str):
            # The original substring semantic is preserved: a string that's a
            # substring of the full identifier compares equal.
            result = self._full_identifier.find(other) > -1
        else:
            # Per the Python data model, returning NotImplemented (rather than
            # raising) lets the other operand's ``__eq__`` try; if neither side
            # can compare, Python falls back to identity comparison and the
            # result is ``False`` without raising.
            result = NotImplemented

        return result

    def __str__(self):
        """
            Returns a string representation for this identifier.

            :returns: The identity string.
        """
        return self.identity