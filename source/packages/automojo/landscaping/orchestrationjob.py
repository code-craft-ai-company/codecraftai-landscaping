"""
    .. module:: orchestrationjob
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the orchestrationjob functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os

from automojo.foundation.collections.contextuser import ContextUser

from automojo.foundation.runtime.runtimevariables import AM_RUNTIME_VARIABLES

from automojo.foundation.runtime.paths import get_path_for_output

from automojo.landscaping.wellknown import LandscapeSingleton

class OrchestrationJob(ContextUser):

    name = "" # Friendly name for the test job
    title = "" # A descriptive title for the test job
    description = "" # Description of the job
    owner = "" # The owning individual or team

    requires_landscape = False
    requires_topology = False
    requires_runtime = False
    requires_credentials = False

    def __init__(self, logger):
        self._logger = logger

        self._starttime = None
        self._stoptime = None

        self._apod = AM_RUNTIME_VARIABLES.AM_AUTOMATION_POD
        self._release = AM_RUNTIME_VARIABLES.AM_BUILD_RELEASE
        self._branch = AM_RUNTIME_VARIABLES.AM_BUILD_BRANCH
        self._build = AM_RUNTIME_VARIABLES.AM_BUILD_NAME
        self._flavor = AM_RUNTIME_VARIABLES.AM_BUILD_FLAVOR
        self._build_url = AM_RUNTIME_VARIABLES.AM_BUILD_URL

        self._run_id = AM_RUNTIME_VARIABLES.AM_RUN_ID

        self._pipeline_id = AM_RUNTIME_VARIABLES.AM_PIPELINE_ID
        self._pipeline_name = AM_RUNTIME_VARIABLES.AM_PIPELINE_NAME
        self._pipeline_instance = AM_RUNTIME_VARIABLES.AM_PIPELINE_INSTANCE

        self._job_initiator = AM_RUNTIME_VARIABLES.AM_JOB_INITIATOR
        self._job_id = AM_RUNTIME_VARIABLES.AM_JOB_ID
        self._job_label = AM_RUNTIME_VARIABLES.AM_JOB_LABEL
        self._job_name = AM_RUNTIME_VARIABLES.AM_JOB_NAME
        self._job_owner = AM_RUNTIME_VARIABLES.AM_JOB_OWNER
        self._job_seed = AM_RUNTIME_VARIABLES.AM_JOB_SEED
        self._job_type = AM_RUNTIME_VARIABLES.AM_JOB_TYPE
        self._job_venue = AM_RUNTIME_VARIABLES.AM_JOB_VENUE
        self._job_tag = AM_RUNTIME_VARIABLES.AM_JOB_TAG

        return


    def begin(self):

        self._starttime = AM_RUNTIME_VARIABLES.AM_STARTTIME

        self._orch_results_dir = get_path_for_output()

        self._runtime_archive = os.path.join(self._test_results_dir, "runtime-declared.yaml")

        return

    def execute(self) -> int:

        result_code = 0

        self._logger.section("Discovery")

        # Initiate contact with the TestLandscape
        self.fire_activate_configuration()

        # STEP 3: Call attach_to_framework on the sequencer to give all the couplings a chance
        # to plug themselves into the automation framework.  This allows us to only integrate
        # couplings that are being consumed by the tests AND also to only include couplings that
        # are included in the test framework.  This give the opportunity for the couplings to trigger
        # the startup of the coordinators that inter-operate with the test landscape and the
        # associated devices.
        self.fire_attach_to_framework()

        # STEP 4: Now that we have collected all the couplings and have a preview of
        # the complexity of the automation run encoded into the coupling types collected.
        # Allow the couplings to attach to the automation environment so they can get
        # a preview of the parameters and configuration and provide us with an early
        # indicator of any parameter or configuration issues.
        #
        # This is the final step of validating all the input information to the run and
        # we are able to perform this step in the context of the integration code and
        # outside of the execution of any test code
        self.fire_attach_to_environment()

        # STEP 5: After all the couplings have had the opportunity to plug themselves into
        # the test framework, we trigger the finalization of the test landscape initialization
        self.fire_activate_integration()

        # STEP 6: All the couplings have had a chance to analyze the configuration
        # information and provide us with a clear indication if there are any configuration
        # issues.  Now provide the couplings with the opportunity to reach out to the
        # automation infrastructure and checkout or collect any global shared resources
        # that might be required for this automation run.
        self._logger.section("Collecting Resources")


        return result_code

    def fire_activate_configuration(self):
        """
            Activating the configuration will load all the configuration information.
        """
        
        landscape = LandscapeSingleton()

        landscape.activate_configuration()

        return

    def fire_attach_to_framework(self):
        """
            Goes through all the integrations and provides them with an opportunity to
            attach to the test environment.
            
            ..note: Attaching to the framework is an internal operation where the intergrations make calls
            on the landscape object or test framework.
        """

        return
    
    def fire_attach_to_environment(self):
        """
            Goes through all the integrations and provides them with an opportunity to
            attach to the test environment.

            ..note: Attaching to the environment is an external operation where the job provides the different
            coordinators that align with the job an opportunity to contact external devices in the environment.
        """

        return

    def fire_activate_integration(self):
        """
            After all the integrations have had an opportunity to attache to the environment and are ready, then we
            finalize the integration phase and activate the integrations.
        """

        landscape = LandscapeSingleton()

        landscape.activate_integration()

        return
    
    def fire_orchestrate_configure_devices(self):
        """
            After we activate all the integrated devices, we can then have all the coordinators go out and orchestrate the configuration
            process for the devices that each coordinator owns.
        """

        landscape = LandscapeSingleton()

        landscape.orchestrate_configure_devices()

        return