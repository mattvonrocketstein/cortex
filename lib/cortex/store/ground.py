""" cortex.store.ground

      smart datastructures for storage
"""

import copy
import datetime

from lindypy.TupleSpace import TSpace
from lindypy.TupleSpace import Client, tuplespace

from cortex.core.util import report
from cortex.core.data import NOT_FOUND_T
from cortex.core.hds import HierarchicalData
from cortex.core.atoms import PersistenceMixin
from cortex.store.tuplespace import CortexTSpace
from cortex.store.mixins import TransformerMixin

class Memory(CortexTSpace, PersistenceMixin, TransformerMixin):
    """ The memory object can hopefully be used just like the data-store you need,
        whatever it is. It morphs into a linda-style tuplespace / "shared blackboard",
        a distributed hash table, or publish/subscribe style event bus.  It is
        embeddable insofar as it supports explicitly named subspaces, allowing
        everyone to see only the section they are interested in, or selectively
        sync/update that subspace.
    """

    universe = None
    __init_tspace = TSpace.__init__

    @property
    def default_name(self):
        """ """
        return '{owner} :: {name}'.format(owner=str(self.owner), name=str(id(self.owner)))

    def _init_memory(self):
        """ """
         # Sign it
        self.john_hancock()

    def _init_subspaces(self, parent_space=None):
        """ NOTE: many times this cannot be called in __init__ because,
                  for example, (universe|'linda').start() would have had to
                  have been finished before cortex.services.postoffice.__init__()
                  had even started... for this reason i suggest calling the function
                  at the beginning of <start>
        """
        # request that parents install me as a subspace.
        subspace_success = (parent_space is not None) and \
                           (parent_space.install_subspace(self))
        report("SubspaceCreation: ", subspace_success)

    def __init__(self, owner, name=None, filename=None, parent_space=None):
        """ """
        self.owner        = owner
        self.parent_space = parent_space
        self.name         = name or self.default_name

        self.__init_persistence(filename)
        self.__init_tspace()
        self._init_memory()

    def __repr__(self):
        """ """
        return "<Memory@"+str(self.owner)+'>'

    def john_hancock(self):
        """ Sign it. """
        self.add(('__name__',  self.name))
        self.add(('__subspaces__',)) # required by subspace mixin
        self.add(('__stamp__', str(datetime.datetime.now())))

    def shutdown(self):
        """ TODO: proxy to TSpace shutdown? what does it do? """
        report("Shutting down Memory.")

    def serialize(self):
        """ from persistenceMixin """
        _str = pickle.dumps(self.values())
        return _str

    def save(self):
        """ from persistenceMixin """
        report('persisting memory to', self.filename)
        PersistenceMixin.save(self.filename)
        report('persisted memory to', self.filename)

    def __init_persistence(self,filename):
        """ persistence mixin """
        if not filename:
            universe = self.owner.universe
            if universe:
                filename = universe.tmpfile().name
        else:
            self.filename = filename
