""" cortex.services.goalmonitor

      a simple service that

      TODO:
"""

from cortex.core.util import report
from cortex.core.service import Service
from cortex.core.atoms import Threadpooler
class GoalMonitor(Threadpooler, Service):
    """ Goal Service:

          Stuff stuff stuff..

          start: brief description of service start-up here
          stop:  brief description service shutdown here

          TODO: either wrap TupleBus.publish up in something asynchronous,
                or guarantee that subscriber-callbacks are themselves
                non-blocking.
    """
    def __init__(self, *args, **kargs):
        """ """
        DIE = lambda: [self.stop(), self.universe.halt()]
        self.goal_tests = kargs.pop('goals',[])
        self.success_action = kargs.pop('success', DIE)
        Service.__init__(self, *args, **kargs)

    #@Threadpooler.reentrant
    def iterate(self):
        if all([ predicate() for predicate in self.goal_tests ]):
            report("ALL GOALS SATISIFIED")
            self.success_action()
