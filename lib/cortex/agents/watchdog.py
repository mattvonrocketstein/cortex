""" cortex.core.agents.watchdog
"""

import warnings

from cortex.core.node import Agent

class WatchDog(Agent):
    def _post_init(self, goals=[], success= None, **kargs):
        self.goal_tests = goals
        if success and getattr(self, 'bark'):
            warn = "success function was passed in, but this class already has a bark() method!: "+str(self.__class__)
            warnings.warn(warn)
        if success:
            setattr(self,  'bark', success)

    def iterate(self):
        """ """
        if all([ predicate() for predicate in self.goal_tests ]):
            self.bark()
