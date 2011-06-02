""" tests for cortex

    turns out the best place to run tests are
    to be inside the system that's being tested..
"""

## Test-classes to use
## TODO: discover these so the list doesn't have to be touched..
from cortex.tests.core_metaclasses import MetaclassesTest
from cortex.tests.core_universe import UniverseCheck
from cortex.tests.core_channels import ChannelCheck
from cortex.tests.core_agent import AgentCheck
from cortex.tests.agents_watchdog import WatchdogTest
bases = (MetaclassesTest, AgentCheck,
         WatchdogTest,    UniverseCheck,
         ChannelCheck, )

## Parameters for the services.. empty and ready to override
#interactive = True                                   # Whether to run shell
interactive = False                                  # Whether to run shell
post_args   = {}                                     # Postoffice parameters
term_args   = {}                                     # Cortex-Terminal arguments
linda_args  = {}                                     # Linda (tuplespace) parameters
test_args   = dict(bases=bases)                      # Parameters for unit-test service

# why did i need this import again?
# otherwise it won't be registered as a service?
from cortex.services.unittesting import UnitTestService

## Build a list of instructions recognizable to the cortex api.  Order does not matter
## here because the service definitions specify (and resolve) their own dependencies.
instructions         = [[ "load_service", ("_linda",),         linda_args ],
                        [ "load_service", ("postoffice",),     post_args  ],
                        [ "load_service", ("unittestservice",),    test_args  ],]
terminal_instruction = [[ "load_service", ("terminal",),       term_args  ],]
if interactive: instructions += terminal_instruction

from cortex.core import api

# Specify terminating conditions to declare as goals
# Declare goals, load services with the given parameters, and invoke mainloop
tests_are_finished_running = lambda: (api.universe|'UnitTestService').stopped
api.declare_goals( [ tests_are_finished_running ] )
api.do( instructions )
api.universe.play()
