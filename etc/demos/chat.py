""" example boot script for cortex
"""

from cortex.core import api
from cortex.core.node import Agent

class Chat(Agent):
    def comment_processor(self, source, *args, **kargs):
        """ A new input processor for the terminal.. will only
            be used when lines start with '#'
        """
        for name,peer in self.universe.peers.items():
            if 'self' != peer.host:
                peer.api.chat( source + ' -- '+self.universe.name)

    def setup(self):
        """ """
        terminal = (self.universe|'terminal')
        comment_predicate = lambda source: source.strip().startswith('#')
        terminal.attach_proc(self.comment_processor, comment_predicate)


# Parameters for the services. mostly empty and ready to override
term_args  = {'syndicate_events_to_terminal' : False}  # Cortex-Terminal arguments: be quiet
api_args   = {}                                        # Arguments for the API-serving daemon
linda_args = {}                                        # Linda (tuplespace) parameters
map_args   = {}                                        # Network-mapper parameters
post_args  = {}                                        # Postoffice parameters
chat_args  = dict(kls=Chat)                            # Chat-agent parameters

# Loads the services with the given parameters.  Order does not
# matter here because the service definitions specify (and resolve)
# dependancies.
api.do( [
        [ "load_service", ("api",),            api_args   ],
        [ "load_service", ("_linda",),         linda_args ],
        [ "load_service", ("terminal",),       term_args  ],
        [ "load_service", ("postoffice",),     post_args  ],
        [ "load_service", ("network_mapper",), map_args   ],
        ])

# Builds the chat-agent described above.
api.do([ ["build_agent", ('test-agent',), chat_args], ])

# Make another copy.. we need someone to talk to.  See how
# __file__ is availible, just like python sans cortex?
# If you want, <clone> is safe to call more than once.
api.clone(file=__file__)


# Invoke the universe (mainloop)
api.universe.play()
