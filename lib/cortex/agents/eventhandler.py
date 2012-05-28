""" cortex.agent.eventhandler
"""

from cortex.core.agent import Agent
from cortex.mixins import LocalQueue
from cortex.core.data import EVENT_T, PEER_T

class AbstractEventHandler(LocalQueue, Agent):
    """ AbstractEventHandler """

    class Meta:
        subscriptions = {EVENT_T: 'push_q',PEER_T: 'push_q'}

    def start(self):
        self.init_q() # safe to call in start or __init__
        super(AbstractEventHandler, self).start()

    def iterate(self):
        """ """
        e = self.pop_q()
        if e:
            self.handle_event(e)

    def handle_event(self, e):
        raise TypeError('not implemented error')
