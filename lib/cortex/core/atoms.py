""" cortex.core.atoms
"""

import pickle
from cortex.core.util import report
from cortex.core.util import report, console

class PersistenceMixin:
    """ """
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

def is_persistent(obj):
    """ dumb helper.. """
    return PersistenceMixin in obj.__class__.__bases__

class AutonomyMixin:
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
              <start> is an invoker, or a mainloop
        """
        report("starting")
        self.started     = True
        self.is_stopped  = False

    def stop(self):
        """ Convention:
              <stop> is a halter
        """
        report("stopping")
        self.is_stopped = True
        self.started    = False

    def play(self):
        """ Convention:
             Responsibilities:
               + invoke <start>, but maybe not right away.
               + never block, and
               + always return "self"

        """
        report("play for "+self.name)
        self.started = True
        self.is_stopped = False

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
            self suitable for acurate transmission/storage elsewhere
        """
        report("darkly for "+self.name)
    shadow = shadowed = darkly
