""" cortex.mixins.flavors

      Describes some different flavors of concurrency that
      can be plugged into cortex agents.

"""
import time
import threading
from cortex.mixins.autonomy import Autonomy
class Eventful(Autonomy):
    pass

class ReactorRecursion(Autonomy):
    """ """
    def run(self):
        #return
        print 't',threading.enumerate()
        from twisted.internet.task import LoopingCall
        LoopingCall(self.run_primitive).start(.01)
        #this speeds up startup time but breaks tests.
        #self.universe.reactor.callLater(self.iteration_period,
        #                                lambda: LoopingCall(self.run_primitive).start(.3))

#self.universe.reactor.callFromThread(self.run_primitive)
        #self.universe.reactor.callLater(self.iteration_period, self.run)
        #self.run_primitive()

    def start(self):
        """ autonomy override """
        Autonomy.start(self)
        # stop wont work if you don't use callFromThread?
        go = lambda: self.universe.reactor.callFromThread(self.run)
        self.universe.reactor.callWhenRunning(self.run)


class Threadpooler(Autonomy):
    """
         will be run in a thread from the twisted threadpool

         if the subclass wrote iterate() as a
           generator, exhaust it and then decide
             whether to stop based on self.iterate.reentrant

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

## A few ready-made combinations
from cortex.core.agent import Agent
class ThreadedAgent(Threadpooler, Agent): pass
class RecursiveAgent(ReactorRecursion, Agent): pass
