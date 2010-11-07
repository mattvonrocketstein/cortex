""" cortex.core.atoms
import pickle

from cortex.core.util import report
from cortex.core.util import report, console

class PersistenceMixin:
    def serialize(self):
        _str = pickle.dumps(self)
        return _str
    def save(self, fname=None):
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

class AutonomyMixin:
    def play(self):
        report("play for "+self.name)
    def resume(self):
        report("resume for "+self.name)
    def pause(self):
        report("pause for "+self.name)
    def freeze(self):
        report("freeze for "+self.name)
    def boot(self):
        report("boot for "+self.name)
        if self.is_local:
            Universe.launch_instance(self)
        else:
            raise NodeError,"Only node-local's can be booted at this time."

class PerspectiveMixin:
    def darkly(self):
        report("darkly for "+self.name)
"""

################

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

class AutonomyMixin:
    """ """
    def sleep(self):
        """ Convention: <sleep> is <stop> & <persist> & <exit>
        """
        report("sleep for "+self.name)
        self.stop()
        if PersistenceMixin in self.__class__.__bases__:
           self.persist()
        self.exit()
        return "Wakeup-Handle Placeholder"

    def start(self):
        """ Convention:
              <start> is an invoker, or a mainloop
        """
        report("starting")

    def stop(self):
        """ Convention:
              <stop> is a halter
        """
        report("stopping")
        self.is_stopped = True
        self.started    = False

    def play(self):
        """ Convention:
             runs <start>, but maybe not right away
        """
        report("play for "+self.name)
        self.started = True

    def resume(self):
        """ Convention:
             <resume> re-enters <start>
        """
        report("resume for "+self.name)

    def pause(self):
        """ Convention:
              <pause> exits <start>
        """
        report("pause for "+self.name)

    def freeze(self):
        """ Convention:
              <freeze> is <stop> & <persists>
        """
        report("freeze for "+self.name)
        self.stop()
        if PersistenceMixin in self.__class__.__bases__:
            self.persist()

    def boot(self):
        """ """
        raise Exception,'niy'
        report("boot for "+self.name)
        if self.is_local:
            Universe.launch_instance(self)
        else:
            raise NodeError,"Only node-local's can be booted at this time."

class PerspectiveMixin:
    def darkly(self):
        """ if this host refers to a local version, obtain an image of
            self suitable for acurate transmission/storage elsewhere
        """
        report("darkly for "+self.name)
