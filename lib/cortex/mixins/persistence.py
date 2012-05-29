""" cortex.mixins.persistence
"""

import pickle

from cortex.core.util import report
from cortex.mixins.mixin import Mixin


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
        if not fname:
            if hasattr(self, 'universe'):
                fname = self.universe.tmpfname()
            elif hasattr(self,'tmpfile'):
                fname = self.tmpfile
        if not fname:
            raise Exception, 'no way to derive fname'
        report('persisting memory@{1} to {2}', self, fname)
        _str = self.serialize()
        with open(fname, 'w') as ___f:
            ___f.write(_str)
        report('persisted memory to', fname)
        return fname

PersistenceMixin=Persistence

def is_persistent(obj):
    """ dumb helper.. """
    return PersistenceMixin in obj.__class__.__bases__
