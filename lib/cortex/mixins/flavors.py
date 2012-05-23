""" cortex.mixins.flavors

    Describes some different flavors of concurrency that
    can be plugged into cortex agents.

"""
import time
import threading

from twisted.internet.task import LoopingCall

from cortex.core.util import report
from cortex.mixins.autonomy import Autonomy
from cortex.util.namespaces import NSPart
from cortex.util.calltools import callchain

class Eventful(Autonomy): pass

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

from channel import ChannelType
from cortex.core.agent import Agent
from cortex.core.util import getcaller
class Threaded(Autonomy):

    @classmethod
    def from_function(kls, func, return_bus=None):
        """ turns a function into an agent.  you might think
            that you can do this with any agent, but it's a
            little more tricky than that.. functions return,
            so in order to keep those semantics, we insist
            that ``self.parent`` exists and has a bus.  it's
            not really limited to the threaded agent, or even
            a *single* parent (multiple-return is no different
            than multiple-subscribers)
        """
        def _post_init(self, **kargs):
            self.fun_kargs = kargs

        @classmethod
        def bind_result_bus(self, bus):
            self._return_bus = bus

        def run(self):
            r = func(**self.fun_kargs)
            bus = getattr(self, '_return_bus', None)
            if bus is not None:
                bus(r)
            self.stop()

        def fault(self, *args, **kargs):
            super(self.__class__, self).fault(*args, **kargs)
            self.universe.halt()

        def start(self):
            # interpret return_bus as an attribute name
            #  on the parent (the parent must also exist)
            if isinstance(return_bus, basestring):
                parent = getattr(self, 'parent', None)
                if parent is None:
                    try:
                        # You should really make sure that parent is
                        # set, because this magic might not work for you
                        parent = getcaller(3)['self']
                    except:
                        self.fault('agents created with .from_function() '
                                   'need to have a parent that exists ')
                bus = getattr(parent, return_bus, None)
                if bus is None:
                    self.fault('parent should have a return_bus '
                               'in order to return results!')

            elif isinstance(return_bus, ChannelType):
                self._return_bus = return_bus
                super(self.__class__, self).start()
            elif return_bus is None:
                super(self.__class__, self).start()
            else:
                err = "return_bus should be string or channel type"
                self.fault(err)

        name      = 'Agentized:'+func.__name__
        bases     = (kls, Agent)
        namespace = dict(_post_init=_post_init,
                         run=run, fault=fault, start=start,
                         bind_result_bus=bind_result_bus)
        return type(name, bases, namespace)

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
    @classmethod
    def from_class(kls, klazz):
        """ Modifies class to use the ThreadedIterator concurrency flavor.

            WARNING! This works in place, if you don't like that you'll
                     need to make a copy / empty subclass first.
        """
        if kls in klazz.__bases__:
            return klazz
        from cortex.mixins.autonomy import AbstractAutonomy
        ns = NSPart(klazz, dictionaries=False).intersection(NSPart(ThreadedIterator))
        ns = ns.methods

        if 'run' in ns:
            if ns['run'] != AbstractAutonomy.run:
                err = "NonAbstract run already defined for {0}".format(klazz)
                raise Exception, err
        else:
            report('replacing run() method')
            old_run = ns.pop('run')
            klazz.run = kls.run
        if getattr(klazz, 'start'):
            import new
            #report('augmenting start() method')
            old_start = klazz.start
            new_start = callchain([old_start, kls.start])
            new_start = new.instancemethod(new_start, None, klazz)
            #def new_start(self):
            #    old_start(self)
            #    kls.start(self)
            klazz.start = new_start
        #else:
        #    report(""
        #report("augmenting __bases__")
        klazz.__bases__ += (kls,)
        return klazz

    def run(self):
        """ see docs for ThreadedIterator """
        while self.started:
            time.sleep(self.iteration_period)
            self.run_primitive()

## A few ready-made combinations
from cortex.core.agent import Agent
class ThreadedAgent(ThreadedIterator, Agent): pass
class RecursiveAgent(ReactorRecursion, Agent): pass
