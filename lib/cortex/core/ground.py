""" cortex.core.ground

      smart datastructures for storage
"""
import datetime

from lindypy.TupleSpace import TSpace
from lindypy.TupleSpace import Client,tuplespace

from cortex.core.atoms import PersistenceMixin

class Memory(TSpace, PersistenceMixin):
    """ A thin wrapper around lindypy's tuplespace. """

    universe = None

    def __init__(self, owner, name=None, filename=None):
        """ """
        self.owner = owner
        self.name  = name or (str(owner) + ' :: ' + str(id(owner)))

        # persistence mixin
        if not filename:
            universe = self.owner.universe
            if universe:
                filename = universe.tmpfile().name
        else:
            self.filename = filename

        TSpace.__init__(self)

        self.john_hancock()

    def john_hancock(self):
        """ Sign it. """
        self.add(('__name__',  self.name))
        self.add(('__stamp__', str(datetime.datetime.now())))

    def as_keyspace(self, name=None):
        """
            NOTE: this is a cheap, stupid, and possibly error-prone
                  cloning operation that is running.. but the alternative
                  is very expensive
        """
        import copy
        name = name or (self.name+':as:Keyspace')
        k = type('dynamicKeyspace',(Keyspace,),{})(self,name=name)
        k.__dict__ = self.__dict__ #copy.copy(self.__dict__)
        return k

    def asdf__getattr__(self,name):
        print 'mem: getattr fail', name

    def shutdown(self):
        """ TODO: proxy to TSpace shutdown? """
        report("Shutting down Memory.")

    def serialize(self):
        """ """
        _str = pickle.dumps(self.values())
        return _str

    def save(self):
        """ """
        report('persisting memory to', self.filename)
        PersistenceMixin.save(self.filename)
        report('persisted memory to', self.filename)

    def get_many(self, pattern):
        """ """
        out=[]
        while True:
            try:
                out.append(self.get(pattern,remove=True))
            except KeyError:
                break
        return out

    #@cache these
    def filter(self, *tests):
        """ """
        out = []
        for item in iter(self.values()):
            passes = True
            for test in tests:
                if not test(item):
                    passes = False
            if passes: out.append(item)
        return out

    def values(self):
        """ """
        #print 'valued'
        return TSpace.values(self)

    def get(self, *args, **kargs):
        """ """
        #print 'get', args, kargs
        return TSpace.get(self, *args, **kargs)

    def add(self, *args, **kargs):
        """ """
        #print 'added', args, kargs
        return TSpace.add(self, *args, **kargs)

class DefaultKeyMapper(object):
    """ The trivial protocol for mapping a tuplespace to a keyspace
    """
    def tuple2key(self,t):
        """ """
        return t[0]

    def tuple2value(self,t):
        """ """
        return t[1:]

    def __setitem__(self, key, value):
        """ dict compat """
        self.add((key, value))

class Keyspace(Memory, DefaultKeyMapper):
    """ Thin wrapper around <Memory> to make it look like a dictionary
    """
    def __contains__(self,other):
        return other in self.keys()

    def keys(self):
        """ dict compat """
        return [ self.tuple2key(x) for x in self.values() ]

    def __getitem__(self, other):
        return self.filter(lambda x: x==other)

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        """ dict compat """
        return [ [ self.tuple2key(x), self.tuple2value(x) ] for x in self.values() ]

    def asdf__getitem__(self,key):
        """ transparent encryption, serialization, perspective warping? """
        pass
