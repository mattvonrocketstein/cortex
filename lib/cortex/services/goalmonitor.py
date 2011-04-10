""" cortex.services.goalmonitor

      a simple service that performs an action after all it's goals are met.

      TODO:
"""

from cortex.core.util import report
from cortex.core.service import Service
from cortex.core.atoms import Threadpooler
from cortex.agents.watchdog import WatchDog

class GoalMonitor(WatchDog, Service, Threadpooler,):
    """ Goal Service:

          Stuff stuff stuff..

          start: brief description of service start-up here
          stop:  brief description service shutdown here

          TODO: have this extend the watchdog agent

          TODO: either wrap TupleBus.publish up in something asynchronous,
                or guarantee that subscriber-callbacks are themselves
                non-blocking.
    """
    def bark(self):
        report("ALL GOALS SATISIFIED")
        self.stop()
        self.universe.halt()
