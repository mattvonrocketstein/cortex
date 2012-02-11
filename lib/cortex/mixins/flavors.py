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

class Threaded(Autonomy):

    @classmethod
    def from_function(kls, func):
        """ turns a function into an agent.  you might think
            that you can do this with any agent, but it's a
            little more tricky than that.. functions return,
            so in order to keep those semantics, we insist
            that ``self.parent`` exists and has a bus.  it's
            not really limited to the threaded agent, or even
            a *single* parent (multiple-return is no different
            than multiple-subscribers)
        """
        from cortex.core.agent import Agent
        class TMP(kls, Agent):
            def _post_init(self, **kargs):
                print 'post_init'
                self.fun_kargs = kargs

            def run(self):
                print 'run'
                r = func(**self.fun_kargs)
                self.parent.bus(r)
        return TMP

    def start(self):
        """ autonomy override """
        Autonomy.start(self)
        go = lambda: self.universe.threadpool.callInThread(self.run)
        self.universe.reactor.callWhenRunning(go)

class ThreadedIterator(Threaded):

    """
         will be run in a thread from the twisted threadpool

         if the subclass wrote iterate() as a
           generator, exhaust it and then decide
             whether to stop based on self.iterate.reentrant

         TODO: save answer in some way?
    """
    def run(self):
        """ see docs for ThreadedIterator """
        while self.started:
            time.sleep(self.iteration_period)
            self.run_primitive()

## A few ready-made combinations
from cortex.core.agent import Agent
class ThreadedAgent(ThreadedIterator, Agent): pass
class RecursiveAgent(ReactorRecursion, Agent): pass
