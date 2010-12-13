""" example boot script for cortex:
    card-game playing agents, first implementations.

    This version should take an approach where the problem is
    defined by the interactions between agent behaviours, ie,
    the agents are defined and the problem is implicit.
"""

from cortex.core import api
from cortex.agents.turntaker import TurnTaker
from cortex.agents.turntaker import TurnTakingGroup

from cortex.core.data import EVENT_T
from cortex.core.bus import handles_event, event
from cortex.util.decorators import afterwards_emit
from cortex.core.bus import handles_and_consumes_event

CUT_CARDS = event("CUT_CARDS")
CARDS_CUT = event("CARDS_CUT")
CARD_GAME = TurnTakingGroup('CardPlayers')
CARDS     = [X for X in "ABCDEFGHIJKLMNOPQRSTUV"]

class Player(TurnTaker):

    #@afterwards_emit(CARDS_CUT)
    @handles_and_consumes_event(CUT_CARDS)
    def cut_cards_request(self, postoffice, cards):
        """ handles and consumes the cut-cards request,
            which will be emitted from the dealer.. after
            the event has been noticed by this player, no
            other player should be notified about/allowed
            to handle the event.

              NOTE: dealer may be in a non-local universe.

        """
        report("Handling cut-cards-request")#, cards)
        N = len(cards)/2;
        first_half = cards[N:]
        second_half = cards[:N]
        result = first_half + second_half
        (self.universe|'postoffice').publish(CARDS_CUT, result)

    class Meta:
        turn_taking_group = CARD_GAME
        class Goals:
            def high_score(self):
                """ defines high-score-goal: NIY """


class Dealer(Player):
    """
        TODO: ensure the dealer may not cut the cards..
              he's a player but a special player
    """

    @afterwards_emit(CUT_CARDS)
    def shuffle_cards(self):
        """ Typically the dealer shuffles alone,
            but since these are robots and the deck
            can get arbitrarily large, we will say
            that all players get to help shuffle
        """
        import random
        global CARDS
        random.shuffle(CARDS)
        return CARDS

    @handles_and_consumes_event(CARDS_CUT)
    def collect_cards(self,postoffice, cards):
        """ """
        report("Collecting cards")
        self.deal_cards(cards)

    def deal_cards(self, cards):
        """ """


    class Meta:
        """ dealer inherits goals from player, but
            the most goals should be ordered by localness
            of the context of their definitions. this way
            of organizing things implies that the universe
            itself may have goals, etc.
        """
        turn_taking_group = CARD_GAME
        class Goals:
            def ready_to_play(self):
                """
                    the cards are shuffled,
                    the cards are cut,
                    the deal is finished
                    the play-order is agreed-upon
                """
                NIY



# Parameters for the services. mostly empty and ready to override
term_args  = {'syndicate_events_to_terminal' : True}  # Cortex-Terminal arguments: be quiet
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
#import IPython; embedshell = IPython.Shell.IPShellEmbed(argv=['-noconfirm_exit']); embedshell()
api.universe.play()
