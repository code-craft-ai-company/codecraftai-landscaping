"""
    .. module:: testjob
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing :class:`LandscapeTestJob`, the landscaping-tier
               base class for test jobs that run against a landscape-managed
               environment.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.integrationruntime.integratedtestjob import IntegratedTestJob
from ccai.testbase.sequencing.testsequencer import TestSequencer

from ccai.landscaping.landscape import Landscape
from ccai.landscaping.wellknown import LandscapeSingleton


class LandscapeTestJob(IntegratedTestJob):
    """
        Landscaping-tier test-job base class.

        Extends :class:`ccai.integrationruntime.integratedtestjob.IntegratedTestJob`
        (the integration tier — JSOS/HTML/presence-folder result recording, run
        metadata from ``RuntimeVariables``) with the **landscape-activation
        lifecycle** required by any test job that runs against a real environment
        described through the landscape model — devices, services, coordinators,
        control points, integration couplings.

        The lifecycle lives HERE, in the package that owns the landscape model.
        The near-standalone testbase :class:`TestJob.execute` fires only the two
        generic attachment hooks, so the landscape-specific phases hang off those
        hooks in this class, preserving the original framework ordering.  Lower
        tiers stay landscape-free: testbase runs standalone, and
        ``codecraftai-interop`` is a base the landscaping package builds ON TOP
        of, so a landscape-aware job there would poison interop tests that have
        no landscape at all.
    """

    def _get_landscape(self) -> Landscape:
        """
            Returns the singleton :class:`Landscape` instance the environment is
            built from.  Override to supply a differently-sourced landscape.

            :returns: The active :class:`Landscape`.
        """
        landscape = LandscapeSingleton()
        return landscape

    def fire_attach_to_framework(self, tseq: TestSequencer) -> None:
        """
            Initiates contact with the landscape and attaches the couplings to
            the automation framework.

                1. ``activate_configuration`` -- the landscape declaration is
                   loaded and validated BEFORE any coupling can ask for device
                   configurations.
                2. ``attach_to_framework`` -- couplings plug themselves into the
                   framework and receive the landscape.
                3. ``activate_integration`` -- the landscape integration layer is
                   finalized now that every participating coupling is known.

            :param tseq: The sequencer controlling the test run.

            :returns: ``None``
        """
        self.fire_activate_configuration()
        landscape = self._get_landscape()
        tseq.attach_to_framework(landscape=landscape)
        self.fire_activate_integration()
        return

    def fire_attach_to_environment(self, tseq: TestSequencer) -> None:
        """
            Attaches the couplings to the live environment and carries the
            landscape through the remainder of its activation lifecycle.

                1. ``attach_to_environment`` -- couplings validate the landscape
                   configuration and surface parameter issues early.
                2. ``collect_resources`` -- couplings check out or collect any
                   global shared resources required for the run.
                3. ``activate_operations`` -- the landscape transitions to fully
                   active, where all device APIs (including connectivity) are
                   available.
                4. ``establish_presence`` -- couplings establish persistent
                   functionality or services on the remote devices.

            :param tseq: The sequencer controlling the test run.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        tseq.attach_to_environment(landscape=landscape)
        tseq.collect_resources()
        self.fire_activate_operations()
        tseq.establish_presence()
        return

    def fire_activate_configuration(self) -> None:
        """
            Activates the configuration phase of the landscape.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        landscape.activate_configuration()
        return

    def fire_activate_integration(self) -> None:
        """
            Activates the integration phase of the landscape.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        landscape.activate_integration()
        return

    def fire_activate_operations(self) -> None:
        """
            Activates the operations phase of the landscape.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        landscape.activate_operations()
        return
