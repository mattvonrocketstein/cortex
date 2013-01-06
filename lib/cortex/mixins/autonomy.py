""" cortex.mixins.autonomy
"""

import time
from types import GeneratorType

from cortex.core.util import report
from cortex.mixins.mixin import Mixin
from cortex.mixins.persistence import is_persistent

class AbstractAutonomy(Mixin):
    """ """

    is_stopped  = False
    started     = False

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

            Responsibilities:
                + invoke <setup> first, if present
                + invoke <start>, but maybe not right away.
                + never block, and
                + always return "self"
        """
        # first setup if it's around
        # start by default does nothing but set flags, so the
        # next line ensures that even stupid default agents get to
        # iterate exactly once.  this has the desirable property of
        # making "the trivial agent" reduce to a function.
        if hasattr(self, 'setup'): self.setup()
        self.start()
        if Autonomy not in self.__class__.__bases__:
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
AutonomyMixin = AbstractAutonomy

class Autonomy(AbstractAutonomy):
    """ """
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
            report("Entering generator", header='')
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
