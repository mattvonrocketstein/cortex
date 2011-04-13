""" cortex.mixins

"""

import pickle
import time
from types import GeneratorType

from cortex.core.util import report, console

class Mixin: pass

class FaultTolerant(Mixin):
    """ faults are a replacement for exceptions """
    def fault(self, error, context):
        """ TODO: sane yet relatively automatic logging for faults.. """
        console.vertical_space()
        report("",header=console.red("--> FAULT <--"))
        console.draw_line()
        print ( "\n{error}".format(error=error))
        import StringIO, pprint
        fhandle = StringIO.StringIO()
        pprint.pprint(context, fhandle)
        print console.color(fhandle.getvalue())
        console.draw_line()
        console.vertical_space()

class AddressMixin:
    """ Something that's addressable """

class Persistence(Mixin):
    """ Something that's persistent """
    def persist(self):
        """ Convention:
             <persist> for "complex" structures is:
               <persist> for self and <persist> for every nontrivial substructure
        """
        report('running persist')

    def serialize(self):
        """ """
        _str = pickle.dumps(self)
        return _str

    def save(self, fname=None):
        """ """
        print fname
        if not fname and hasattr(self, 'universe'):
             fname = self.universe.tmpfile().name
        elif not fname and hasattr(self,'tmpfile'):
            fname = self.tmpfile().name
        else:
            raise Exception,'no way to derive fname'
        report('persisting memory to', fname)
        _str = self.serialize()
        ___f = open(fname,'w')
        ___f.write(_str)
        ___f.close()
        report('persisted memory to', fname)
PersistenceMixin=Persistence

def is_persistent(obj):
    """ dumb helper.. """
    return PersistenceMixin in obj.__class__.__bases__

class Autonomy(Mixin):
    """ """

    def harikari(self):
        """ Convention:
              + <stop> self,
              + <stop> children,
              + <exit> children
              + <exit> self
              + whatever else to ensure-garbage-collection
        """
        pass

    def sleep(self):
        """ Convention: <sleep> is
             + <stop>,
             + <persist>,
             + <exit>
        """
        report("sleep for "+self.name)
        self.stop()

        if is_persistent(self): self.persist()
        else:
            # warn: sleep without persist!
            pass

        self.exit()
        return "Wakeup-Handle Placeholder"

    def start(self):
        """ Convention:
              <start> is an invoker, or a mainloop.

            Note: When invocation is largely separate from mainloop,
            it is suggested to add a <run> for the mainloop which is
            called from <start>. ( Remember: <run> is not guaranteed
            to be called by the framework; call it yourself however
            you wish from your <start>.)
        """
        self.started     = True
        self.is_stopped  = False

    def run(self):
        """ ABSTRACT: See note in ``start`` """

    @property
    def stopped(self):
        """ TODO: single source of truth this.. """
        return self.is_stopped

    def stop(self):
        """ Convention:
              <stop> is a halter
        """
        self.is_stopped = True
        self.started    = False

    def play(self):
        """ Convention:
              <play> should always return something similar to a deferred.
              This is a representation of <self> where <self> has
              fundamentally been *invoked* already and is waiting
              for the universal main loop to begin.

        """
        """ Convention:
              Responsibilities:
                + invoke <start>, but maybe not right away.
                + never block, and
                + always return "self"
        """
        # first setup if it's around
        # start by default does nothing but set flags, so the
        # next line ensures that even stupid default agents get to
        # iterate exactly once.  this makes "the trivial agent"
        # reducible to a function.
        if hasattr(self, 'setup'): self.setup()
        self.start()
        if ConcreteAutonomy not in self.__class__.__bases__:
            self.universe.reactor.callWhenRunning(self.iterate)
        return self

    def resume(self):
        """ Convention:
             <resume> re-enters <start>
        """
        self.started = True
        report("resume for "+self.name)

    def pause(self):
        """ Convention:
              <pause> exits <start>
        """
        self.started = False
        report("pause for " + self.name)

    def freeze(self):
        """ Convention: <freeze> is
              + <stop>
              + <persist>
        """
        report("freeze for "+self.name)
        self.stop()
        if is_persistent(self): self.persist()
AutonomyMixin = Autonomy

class ControllableMixin(Mixin):
    def halt(self):
        """ like "stop" only safe to call from anywhere """
        ABSTRACT


class ConcreteAutonomy(Autonomy):
    @staticmethod
    def reentrant(func):
        func.reentrant=True
        return func

    @property
    def iteration_period(self):
        """ how often to let this agent do things.
            the default is one second.  if you need to
            change this, set _iteration_period for your
            agent or you agents class, or if the value isn't
            static you can  override this property in your
            subclass.

            TODO: make getters and setters; it's better than
                  fooling around with __init__, maybe

        """
        return getattr(self, '_iteration_period', 1)

    def run_primitive(self):
        """ run_primitive does one "tick" worth of <run>.

            this is kind of like <iterate>, but it encapsulates
            logic that would be awkward for subclassers to have
            to put there.
        """
        result = self.iterate()
        if isinstance(result, GeneratorType):
            report("Entering generator",header='')
            try:
                while result: result.next()
            except StopIteration:
                if hasattr(self.iterate, 'reentrant'):
                    pass
                else:
                    self.stop()

    def iterate(self):
        """ Just for example purposes, and to remind
            subclassers to override this method
        """
        msg = "override this: default iteration for threadpooler:"
        report(msg, self)
        yield "arbitrary value"
        # Next line should not block anything..
        #   it's in the threadpool.
        time.sleep(1)
    iterate.reentrant=True

class ReactorRecursion(ConcreteAutonomy):
    """ """
    def run(self):
        self.run_primitive()
        self.universe.reactor.callLater(self.iteration_period, self.run)

    def start(self):
        """ autonomy override """
        Autonomy.start(self)
        go = lambda: self.universe.reactor.callFromThread(self.run)
        self.universe.reactor.callWhenRunning(go)

class Threadpooler(ConcreteAutonomy):
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

class PerspectiveMixin:
    """
    def ground(self):
        ''' placeholder: run filters on the ground here, ie
              + grab only some particular named subspace, or
              + pre-processing, post-processing, misc. mutation
        '''
        return self.universe.ground
    """

    def darkly(self):
        """ if this agent refers to a local version, ie is a nonproxy, obtain
            an image of self suitable for acurate transmission/storage/reinvocation
            elsewhere
        """
        image = self.serialize()
        return NY

    # Aliases
    shadow = shadowed = darkly
