""" example boot script for cortex
"""

from cortex.core import api
#from cortex.core.util import report
from cortex.core.universe import Universe
from cortex.core.node import Agent


class Chat(Agent):

    requires_services = ['terminal']

    def input_proc(self, *args, **kargs):
        """ A new input processor for the terminal.
            It's your usual ipython prompt except that
            lines starting with '#' will be treated as
            chat-text.
        """
        txt = args[0]
        if txt.strip().startswith('#'):
                for name,peer in self.universe.peers.items():
                    if 'self' != str(peer.host):
                        peer.api.chat( txt + ' -- '+self.universe.name)

        else:
            self.original_input_processor(*args, **kargs)

    def setup(self):
        """ When lines start with '#',
             treat them as a chat message. """
        terminal = (self.universe|'terminal')
        self.original_input_processor = terminal.replace_input_processor(self.input_proc)


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
        #[ "load_service", ("terminal",),       term_args  ],  #comment to begin
        [ "load_service", ("postoffice",),     post_args  ],
        [ "load_service", ("network_mapper",), map_args   ],
        ])

#api.do([ ["build_agent", ('test-agent',), dict(kls=Chat, kls_kargs={})], ])
#api.clone(file=__file__)
Universe.play()
