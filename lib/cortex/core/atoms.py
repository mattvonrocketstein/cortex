""" cortex.core.atoms

"""

import pickle
import time
from types import GeneratorType

from cortex.core.util import report, console

class Mixin(object): pass

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
              + <stop> children, and
              + ensure-garbage-collection
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
              Responsibilities:
                + invoke <start>, but maybe not right away.
                + never block, and
                + always return "self"
        """
        #report("play for " + getattr(self, 'name', 'DEFAULT-NAME'))
        self.start()

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

class Threadpooler(Autonomy):
    """
         will be run in a thread from the twisted threadpool

         if the subclass wrote iterate() as a
           generator, exhaust it and then decide
             whether to stop based on self.iterate.reentrant

         TODO: save answer in some way?
    """
    @staticmethod
    def reentrant(func):
        func.reentrant=True
        return func


    @property
    def iteration_period(self):
        """
            TODO: make getters and setters; it's better
                 than having to do something in __init__..

        """
        return getattr(self, '_iteration_period', 1)

    def run(self):
        """ see docs for Threadpooler """
        while self.started:
            time.sleep(self.iteration_period)
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
        msg = "override this: default iteration for threadpooler.."
        report(msg)
        yield "arbitrary value"
        time.sleep(1) # Should not block anything

    iterate.reentrant=True

    def start(self):
        """ autonomy override """
        Autonomy.start(self)
        go = lambda: self.universe.threadpool.callInThread(self.run)
        self.universe.reactor.callWhenRunning(go)

class PerspectiveMixin:
    """
    """
    #def ground(self):
    #    """ placeholder: run filters on the ground here, ie
    #          + grab only some particular named subspace, or
    #          + pre-processing, post-processing, misc. mutation
    #    """
    #    return self.universe.ground

    def darkly(self):
        """ if this host refers to a local version, obtain an image of
            self sui
            table for acurate transmission/storage elsewhere
        """
        report("darkly for "+self.name)
    shadow = shadowed = darkly
