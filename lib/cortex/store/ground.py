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

class Memory(TSpace, PersistenceMixin):
    """ A thin wrapper around lindypy's tuplespace. """

    universe = None

    def __init__(self, owner, name=None, filename=None, parent_space=None):
        """ """
        self.owner = owner
        self.parent_space = parent_space
        self.name  = name or (str(owner) + ' :: ' + str(id(owner)))

        # persistence mixin
        if not filename:
            universe = self.owner.universe
            if universe:
                filename = universe.tmpfile().name
        else:
            self.filename = filename

        TSpace.__init__(self)

        self.john_hancock() # Sign it
        if parent_space is not None:
            parent_space.install_subspace(self)

    def __repr__(self):
        return "<Memory@"+str(self.owner)+'>'

    @property
    def subspaces(self):
        return self.filter(lambda tpl: tpl[0]=='__subspaces__')[0]

    def install_subspace(self, other):
        """ TODO: ensure type(self)==type(other)?
            REFACTOR..
        """

        #sanity check
        existential_test = lambda tpl: tpl[0] == other.name
        search_results   = self.filter(existential_test)
        err = "Already a subspace by the name of {name} in {space} !"
        err = err.format(name=other.name, space=self.name)
        assert not search_results, err

        subspace = (other.name, other)
        self.add(subspace)

        # update subspace list
        subspaces = self.subspaces + (other.name,)
        self.get(self.subspaces, remove=True)
        self.add(subspaces)

        report('finished installing subspace')

    def john_hancock(self):
        """ Sign it. """
        self.add(('__name__',  self.name))
        self.add(('__subspaces__',))
        self.add(('__stamp__', str(datetime.datetime.now())))

    def as_keyspace(self, name=None):
        """ TODO: use cortex.store.transform

            NOTE: this is a cheap, stupid, and possibly error-prone
                  cloning operation that is running.. but the alternative
                  is very expensive
        """
        from cortex.store.keyspace import Keyspace
        name = name or (self.name+':as:Keyspace')
        k = type('dynamicKeyspace', (Keyspace,),{})(self, name=name)
        k.__dict__ = self.__dict__ #copy.copy(self.__dict__)
        return k

    def asdf__getattr__(self,name):
        print 'mem: getattr fail', name

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

    def get_many(self, pattern):
        """ from lindypy """
        out=[]
        while True:
            try:
                out.append(self.get(pattern,remove=True))
            except KeyError:
                break
        return out

    def get(self, *args, **kargs):
        """ from lindypy """
        #print 'get', args, kargs
        return TSpace.get(self, *args, **kargs)

    def add(self, *args, **kargs):
        """ from lindypy """
        #print 'added', args, kargs
        return TSpace.add(self, *args, **kargs)

    #@cache these
    def filter(self, *tests, **kargs):
        """ new """
        remove = kargs.pop('remove', False)
        out    = tuple()
        for item in iter(self.values(safe=True)):
            #item =self.get(item)
            passes = True
            for test in tests:
                if not test(item):
                    passes = False
            if passes:
                out += (item,)
                if remove:
                    self.get(item, remove=remove)
        return out

    def values(self, safe=False):
        """ from lindypy

            NOTE: values can be stale.. safe ensures they are
                  availible to be get'ed and not just ghosts
        """
        out = TSpace.values(self)
        if safe:
            for tpl in out:
                try:
                    self.get(tpl)
                except KeyError:
                    out.remove(tpl)
        return out
