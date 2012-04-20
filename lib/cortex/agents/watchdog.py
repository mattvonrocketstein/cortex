""" cortex.core.agents.watchdog
"""

import warnings

from cortex.core.util import report
from cortex.core.agent import Agent

class WatchDog(Agent):
    """ Watchdog will bark when everything in watch_list tests True.
        He barks with self.bark() or the "success" action he is
        passed on __init__.
    """

    def _post_init(self, watch_list=[], bark= None, **kargs):
        """ NOTE: if "bark" function is passed it will be used,
                  even if there is already a bark() method defined!
        """
        # Sanity check
        if not isinstance(watch_list,(tuple,list)):
            self.fault('watch-list does not look iterable: '+type(watch_list))
        for predicate in watch_list:
            if not callable(predicate):
                self.fault('watch-list contains non-callable: '+str(predicate))


        self.watch_list = watch_list
        if bark and getattr(self, 'bark', None):
            warn  = "bark function was passed in, but this class already has a bark() method!: "
            warn += str(self.__class__)
            warnings.warn(warn)

        if bark:
            setattr(self,  'bark', bark)

    def iterate(self):
        """ watchdog overrides agent iterate """
        if self.watch_list and all([ predicate() for predicate in self.watch_list ]):
            self.bark()
