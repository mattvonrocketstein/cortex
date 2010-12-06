""" example boot script for cortex:
      card-game playing agents, second implementations.

    This version should take an approach using a problem description
    language, where the problem is defined and that descriptions actually
    *generates* the agents that are needed to solve it.
"""
from cortex.util.decorators import handles_event
from cortex.core import api
from cortex.core.node import Agent

#class Cards(Artifact):
#    pass

class Player(Agent):
    #@handles_event
    def cut_cards_request(self, cards):
        pass

    #@handles_event
    def done_dealing(self):
        pass

class Dealer(Agent):
    #@handles_event
    def ready_to_play(self):
        pass

# Parameters for the services. mostly empty and ready to override
term_args  = {'syndicate_events_to_terminal' : False}  # Cortex-Terminal arguments: be quiet
api_args   = {}                                        # Arguments for the API-serving daemon
linda_args = {}                                        # Linda (tuplespace) parameters
map_args   = {}                                        # Network-mapper parameters
post_args  = {}                                        # Postoffice parameters
deal_args  = dict(kls=Dealer)                          # Dealer-agent parameters
#plyr1

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
api.do([ ["build_agent", ('test-agent',), deal_args], ])

# Make another copy.. we need someone to play cards with.
# Notice __file__ is availible, just like python sans cortex?
# If you want, <clone> is safe to call more than once.
# Labels will come out unique no matter how they go in..
#  this allows the original Universe to keep track of it's clones
label = api.clone(file=__file__, label='player')

#macroverse.distribute_workers()

# Invoke the universe (mainloop)
api.universe.play()
