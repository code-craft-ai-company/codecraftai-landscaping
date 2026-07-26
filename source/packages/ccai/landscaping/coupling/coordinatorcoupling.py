"""
    .. module:: coordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`CoordinatorCoupling` class and associated reflection methods.
    The :class:`CoordinatorCoupling` derived classes can be used to integraton automation resources and roles
    into the test environment.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import TYPE_CHECKING

from ccai.errors.exceptions import AbstractMethodError

from ccai.testbase.coupling.integrationcoupling import IntegrationCoupling

if TYPE_CHECKING:
    from ccai.landscaping.landscape import Landscape

class CoordinatorCoupling(IntegrationCoupling):
    """
        The :class:`CoordinatorCoupling` object serves as the base object for the declaration of an
        automation integration coordinator coupling.
    """

    coordinator = None

    landscape = None

    @classmethod
    def attach_to_framework(cls, **kwargs):
        """
            Stores the landscape passed by the test framework on the coupling class so
            derived couplings can reach it in later lifecycle phases.  Landscape
            awareness lives HERE, in the landscaping tier -- the near-standalone
            testbase :class:`IntegrationCoupling` base treats framework attachment as
            an optional no-op.

            :param kwargs: Keyword arguments forwarded by the sequencer; ``landscape``
                is stored on the coupling class when present.

            :returns: None
        """
        if "landscape" in kwargs:
            cls.landscape = kwargs["landscape"]
        return

    @classmethod
    def attach_to_environment(cls, **kwargs):
        """
            Called so the coupling can validate the environment and configuration
            it will run in.  The default is a no-op: coordinator couplings do
            their registration in :meth:`attach_to_framework` (the landscape's
            ``activate_integration`` step needs the registrations before
            environment attachment runs), and most have no further environment
            validation to perform.  Override when a coupling does.

            :param kwargs: Keyword arguments forwarded by the sequencer;
                includes ``landscape``.

            :returns: None
        """
        return

    @classmethod
    def create_coordinator(cls, landscape: "Landscape") -> object:
        """
            This API is called so that the landscape can create a coordinator for a given coordinator
            integration role.
        """
        raise AbstractMethodError("This method must be overridden by derived coordinator classes.")

