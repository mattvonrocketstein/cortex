""" example boot script for cortex
"""

from unittest import TestCase

from cortex.core import api
from cortex.core.node import Agent
from cortex.core.service import Service
from cortex.core.atoms import Threadpooler
from cortex.services.unittesting import SanityCheck
from cortex.core.util import report, console


# Parameters for the services. mostly empty and ready to override
term_args  = {}#'syndicate_events_to_terminal' : False}  # Cortex-Terminal arguments: be quiet
api_args   = {}                                        # Arguments for the API-serving daemon
linda_args = {}                                        # Linda (tuplespace) parameters
map_args   = {}                                        # Network-mapper parameters
post_args  = {}                                        # Postoffice parameters

# Loads the services with the given parameters.  Order does not
# matter here because the service definitions specify (and resolve)
# dependancies.
api.do( [
        #[ "load_service", ("api",),            api_args   ],
        [ "load_service", ("_linda",),         linda_args ],
        [ "load_service", ("terminal",),       term_args  ],
        [ "load_service", ("postoffice",),     post_args  ],
        #[ "load_service", ("network_mapper",), map_args   ],
        [ "load_service", ("sanitycheck",), {}   ],
        ])

# Builds the chat-agent described above.
#api.do([ ["build_agent", ('test-agent',), chat_args], ])

# Make another copy.. we need someone to talk to.  See how
# __file__ is availible, just like python sans cortex?
# If you want, <clone> is safe to call more than once.
#api.clone(file=__file__)


# Invoke the universe (mainloop)
api.universe.play()
