""" cortex.core.agents.watchdog
"""

import warnings

from cortex.core.node import Agent

class WatchDog(Agent):
    """ Watchdog will bark when everything in watch_list tests True.
        He barks with self.bark() or the "success" action he is
        passed on __init__.
    """
    def _post_init(self, watch_list=[], success= None, **kargs):
        """ NOTE: if "success" function is passed it will be used,
                  even if there is already a bark() method defined!
        """
        self.watch_list = watch_list
        if success and getattr(self, 'bark'):
            warn = "success function was passed in, but this class already has a bark() method!: "+str(self.__class__)
            warnings.warn(warn)
        if success:
            setattr(self,  'bark', success)

    def iterate(self):
        """ watchdog overrides agent iterate """
        if self.watch_list and all([ predicate() for predicate in self.watch_list ]):
            self.bark()
