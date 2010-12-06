""" cortex.agents.turntaker
       Abstraction for agents that take turns completing tasks
"""

import types

from cortex.agents import Agent
from cortex.core.metaclasses import TokenFactory

class TurnTaker(Agent):
    def _post_init(self, group=None, turn_taking_group=None):
        """ set the turn-taking-group for this agent """
        group_from_meta = getattr(self.Meta, 'turn_taking_group',None)
        group_from_karg = group = group or turn_taking_group
        group = group_from_karg or group_from_meta
        if group is None:
            err = 'The turn-taking-agent "{A}" should specify the group it belongs to.'
            err = err.format(A=str(self.__class__.__name__))
            raise Exception, err
        else:
            self.group = group

TurnTakingGroup = TokenFactory.new()
