""" example boot script for cortex:
      card-game playing agents, first implementations.

    This version should take an approach where the problem is
    defined by the interactions between agent behaviours, ie,
    the agents are defined and the problem is implicit.
"""


from cortex.core import api
from cortex.core.agent import Agent

from cortex.core.bus import handles_and_consumes_event
from cortex.core.bus import handles_event, event


CUT_CARDS = event("CUT_CARDS")

class Player(Agent):
    class Meta:
        goals = [ high_score ]

    def high_score(self):
        """ defines high-score-goal: NIY """


    @handles_and_consumes_event(CUT_CARDS)
    def cut_cards_request(self, cards):
        """ handles the cut-cards request from dealer

              NOTE: dealer may be in a non-local universe.

        """
        num_cards = len(cards)/2;
        first_half = cards[N:]
        second_half = cards[:N]
        return first_half + second_half


class Dealer(Player):
    """
        TODO: ensure the dealer may not cut the cards..
              he's a player but a special player
    """

    def shuffle_cards(self):
        """ typically the dealer shuffles alone,
           but since these are robots and the deck
           can get arbitrarily large, we will say
           that all players get to help shuffle """
        NIY

    def ready_to_play(self):
        # the cards are shuffled,
        # the cards are cut,
        # the deal is finished

    class Meta:
        """ dealer inherits goals from player, but
            the most goals should be ordered by localness
            of the context of their definitions. this way
            of organizing things implies that the universe
            itself may have goals, etc.
        """
        goals = [ ready_to_play ]


# Parameters for the services. mostly empty and ready to override
term_args  = {'syndicate_events_to_terminal' : False}  # Cortex-Terminal arguments: be quiet
api_args   = {}                                        # Arguments for the API-serving daemon
linda_args = {}                                        # Linda (tuplespace) parameters
map_args   = {}                                        # Network-mapper parameters
post_args  = {}                                        # Postoffice parameters
deal_args  = dict(kls=Dealer)                          # Dealer-agent parameters
play_args  = dict(kls=Player)                          # Player-agent parameters


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
api.do([ ["build_agent", ('dealer-agent',), deal_args], ])
api.do([ ["build_agent", ('player-agent',), play_args], ])

# Make another copy.. we need someone to play cards with.
# Notice __file__ is availible, just like python sans cortex?
# If you want, <clone> is safe to call more than once.
# Labels will come out unique no matter how they go in..
#  this allows the original Universe to keep track of it's clones
#label = api.clone(file=__file__, label='player')

#macroverse.distribute_workers()

# Invoke the universe (mainloop)
api.universe.play()
