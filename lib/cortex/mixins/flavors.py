""" cortex.mixins.flavors

      describes some different flavors of concurrency

"""
import time
from cortex.mixins.autonomy import Autonomy
class ReactorRecursion(Autonomy):
    """ """
    def run(self):
        raise Exception,"RAN"
        self.run_primitive()
        self.universe.reactor.callLater(self.iteration_period, self.run)

    def start(self):
        """ autonomy override """
        Autonomy.start(self)
        go = lambda: self.universe.reactor.callFromThread(self.run)
        self.universe.reactor.callWhenRunning(go)

class Threadpooler(Autonomy):
    """
         will be run in a thread from the twisted threadpool

         if the subclass wrote iterate() as a
           generator, exhaust it and then decide
             whether to stop based on self.iterate.reentrant
         ?
         TODO: save answer in some way?
    """
    def run(self):
        """ see docs for Threadpooler """
        while self.started:
            time.sleep(self.iteration_period)
            self.run_primitive()

    def start(self):
        """ autonomy override """
        Autonomy.start(self)
        go = lambda: self.universe.threadpool.callInThread(self.run)
        self.universe.reactor.callWhenRunning(go)
