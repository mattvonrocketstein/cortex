""" cortex.services.goalmonitor

      A simple service that performs an action after all it's goals are met.
      typically this service is constructed implicitly by calls to the API.

      The following example is taken from cortex.test.__main__,
      aka the unittesting harness.

       >>>  tests_are_finished_running = lambda: \
               (api.universe|'UnitTestService').stopped
       >>>  api.declare_goals( [ tests_are_finished_running ] )
"""

from cortex.core.util import report
from cortex.core.service import Service
from cortex.mixins.flavors import Threadpooler
from cortex.agents.watchdog import WatchDog

class GoalMonitor(WatchDog, Service, Threadpooler,):
    """ the Goal Service is a watchdog who shuts down the
        universe when all it's goals are completed.
    """
    def _post_init(self, goals=[], success=None, **kargs):
        """ alias watchdog's "watch_list" argument
            to "goals" for a more intuitive api.
        """
        kargs.update(dict(watch_list=goals))
        kargs.update(dict(success=success))
        super(GoalMonitor,self)._post_init(**kargs)

    def bark(self):
        """ bark() is called by watchdog when
            everything in the goal_list tests True """
        report("ALL GOALS SATISIFIED")
        self.stop()
        self.universe.halt()
