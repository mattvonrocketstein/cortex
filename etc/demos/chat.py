""" example boot script for cortex
"""

from cortex.core import api
#from cortex.core.util import report
from cortex.core.universe import Universe
from cortex.core.node import Agent


class Chat(Agent):

    requires_services = ['terminal']

    def comment_processor(self, source, *args, **kargs):
        """ A new input processor for the terminal.. will only
            be used when lines start with '#'
        """
        for name,peer in self.universe.peers.items():
            if 'self' != str(peer.host):
                peer.api.chat( source + ' -- '+self.universe.name)

    def setup(self):
        """ """
        terminal = (self.universe|'terminal')
        comment_predicate = lambda source: source.strip().startswith('#'))
        terminal.attach_proc(self.input_proc,comment_predicate)


# Parameters for the services. mostly empty and ready to override
term_args  = {'syndicate_events_to_terminal' : False}  # Cortex-Terminal arguments: be quiet
api_args   = {}                                        # Arguments for the API-serving daemon
linda_args = {}                                        # Linda (tuplespace) parameters
map_args   = {}                                        # Network-mapper parameters
post_args  = {}                                        # Postoffice parameters

# Load services
api.do( [
        [ "load_service", ("api",),            api_args   ],
        [ "load_service", ("_linda",),         linda_args ],
        [ "load_service", ("terminal",),       term_args  ],  #comment to begin
        [ "load_service", ("postoffice",),     post_args  ],
        [ "load_service", ("network_mapper",), map_args   ],
        ])

api.do([ ["build_agent", ('test-agent',), dict(kls=Chat, kls_kargs={})], ])
api.clone(file=__file__)
Universe.play()
