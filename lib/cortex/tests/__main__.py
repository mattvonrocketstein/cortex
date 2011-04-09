""" tests for cortex

    turns out the best place to run tests are
    to be inside the system that's being tested.
"""

from cortex.tests.channel import *



from cortex.core import api
from cortex.services.unittesting import UnitTestService

from cortex.tests.core_universe import UniverseCheck
from cortex.tests.core_channels import ChannelCheck
from cortex.tests.core_agent import AgentCheck
from cortex.tests.agents_watchdog import WatchdogTest

# Test-classes to use
bases = (AgentCheck, WatchdogTest, UniverseCheck, ChannelCheck, )

## Parameters for the services.. empty and ready to override
interactive = True                                  # Whether to run shell
post_args   = {}                                     # Postoffice parameters
term_args   = {}                                     # Cortex-Terminal arguments
linda_args  = {}                                     # Linda (tuplespace) parameters
test_args   = dict(bases=bases)                      # Parameters for unit-test service

## Build a list of instructions recognizable to the cortex api.  Order does not matter
## here because the service definitions specify (and resolve) their own dependencies.
instructions         = [[ "load_service", ("_linda",),         linda_args ],
                        [ "load_service", ("postoffice",),     post_args  ],
                        [ "load_service", ("unittestservice",),    test_args  ],]
terminal_instruction = [[ "load_service", ("terminal",),       term_args  ],]
if interactive: instructions += terminal_instruction

# Specify terminating conditions to declare as goals
tests_are_finished_running = lambda: (api.universe|'UnitTestService').stopped

# Declare goals, load services with the given parameters, and invoke mainloop
api.declare_goals( [ tests_are_finished_running ] )
api.do( instructions )
api.universe.play()
