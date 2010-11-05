""" cortex.core.atoms
"""

import pickle

from cortex.core.util import report
from cortex.core.util import report, console

class PersistenceMixin:
    """ """

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
    def play(self):
        """ """
        report("play for "+self.name)

    def resume(self):
        """ """
        report("resume for "+self.name)
    def pause(self):
        """ """
        report("pause for "+self.name)
    def freeze(self):
        """ """
        report("freeze for "+self.name)
    def boot(self):
        """ """
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
