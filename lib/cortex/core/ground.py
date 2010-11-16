""" cortex.core.ground

      smart datastructures for storage
"""
import datetime

from lindypy.TupleSpace import TSpace
from lindypy.TupleSpace import Client,tuplespace

from cortex.core.atoms import PersistenceMixin

class Memory(TSpace,PersistenceMixin):
    """ A thin wrapper around lindypy's tuplespace. """
    def __init__(self, owner, name=None, filename=None):
        """ """
        self.owner = owner
        self.name  = name or (str(owner) + ' :: ' + str(id(owner)))

        # persistence mixin
        self.filename = filename or self.owner.universe.tmpfile().name
        TSpace.__init__(self)

        self.john_hancock()

    def john_hancock(self):
        """ Sign it. """
        self.add(('__name__',  self.name))
        self.add(('__stamp__', str(datetime.datetime.now())))

    def as_keyspace(self):
        """
            NOTE: this is a cheap, stupid, and possibly error-prone
                  cloning operation that is running.. but the alternative
                  is very expensive
        """

    #def __getattr__(self,name):
    #    return print 'mem: getattr fail', name

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


class Keyspace(Memory):
    """ Thin wrapper around <Memory> to make it look like a dictionary
    """

    def keys(self):
        """ dict compat """
        return iter([x[0] for x in self.values()])

    def items(self):
        """ dict compat """
        return iter([x[0],x[1:]] for x in self.values())

    def __setitem__(self, key, value):
        """ dict compat """
        self.add((key,value))

    def asdf__getitem__(self,key):
        """ transparent encryption, serialization, perspective warping? """
        pass
