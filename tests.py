""" example boot script for cortex
"""

from cortex.core import api
from cortex.core.node import Agent
from cortex.core.service import Service
from cortex.core.util import report, console
from cortex.services.unittesting import SanityCheck


## Parameters for the services.. empty and ready to override
interactive = False                                  # Whether to run shell
post_args   = {}                                     # Postoffice parameters
term_args   = {}                                     # Cortex-Terminal arguments
linda_args  = {}                                     # Linda (tuplespace) parameters
test_args   = {}                                     # Parameters for unit-test service

## Build a list of instructions recognizable to the cortex api.  Order does not matter
## here because the service definitions specify (and resolve) their own dependencies.
instructions         = [[ "load_service", ("_linda",),         linda_args ],
                        [ "load_service", ("postoffice",),     post_args  ],
                        [ "load_service", ("sanitycheck",),    test_args  ],]
terminal_instruction = [[ "load_service", ("terminal",),       term_args  ],]
if interactive: instructions += terminal_instruction

# Specify terminating conditions to declare as goals
tests_are_finished_running = lambda: (api.universe|'sanitycheck').stopped

# Declare goals, load services with the given parameters, and invoke mainloop
api.declare_goals( [ tests_are_finished_running ] )
api.do( instructions )
api.universe.play()
