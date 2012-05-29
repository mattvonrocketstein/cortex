""" cortex.core.ground

      smart datastructures for storage
"""
import sys
import pickle
import datetime

from lindypy.TupleSpace import TSpace

from cortex.core.util import report
from cortex.core.hds import HierarchicalData
from cortex.mixins import PersistenceMixin

class HierarchicalWrapper(HierarchicalData):
    """ """
    def __init__(self, proxy_name):
        super(HierarchicalWrapper,self).__init__()
        self._proxy = proxy_name

    def __getattr__(self, name):
        """ """
        if hasattr(self, '_proxy') and hasattr(self._proxy, name):
            return getattr(object.__getattribute__(self,'_proxy'), name)
        else:
            return super(HierarchicalWrapper,self).__getattr__(name)

class Memory(TSpace, PersistenceMixin):
    """ A thin wrapper around lindypy's tuplespace. """
    """ Memory according to ACT-R cognitive architecture:
        Memory modules. There are two kinds of memory modules in ACT-R:
          o Declarative memory, consisting of facts such as Washington, D.C. is the
            capital of United States, France is a country in Europe, or 2+3=5
          o Procedural memory, made of productions. Productions represent knowledge
            about how we do things: for instance, knowledge about how to type the
            letter "Q" on a keyboard, about how to drive, or about how to perform
            addition.


          All the modules can only be accessed through their buffers. The contents of
          the buffers at a given moment in time represents the state of ACT-R at that
          moment. The only exception to this rule is the procedural module, which
          stores and applies procedural knowledge. It does not have an accessible
          buffer and is actually used to access other module's contents.

          Procedural knowledge is represented in form of productions. The term
          "production" reflects the actual implementation of ACT-R as a production
          system, but, in fact, a production is mainly a formal notation to specify
          the information flow from cortical areas (i.e. the buffers) to the basal
          ganglia, and back to the cortex.

          At each moment, an internal pattern matcher searches for a production that
          matches the current state of the buffers. Only one such production can be
          executed at a given moment. That production, when executed, can modify the
          buffers and thus change the state of the system. Thus, in ACT-R, cognition
          unfolds as a succession of production firings.
    """
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

        self._john_hancock()

    def _john_hancock(self):
        """ Sign it. """
        self.add(('__name__',  self.name))
        #self.add(('__stamp__', str(datetime.datetime.now())))

    def as_keyspace(self, name=None):
        """
            NOTE: this is a cheap, stupid, and possibly error-prone
                  cloning operation that is running.. but the alternative
                  is very expensive
        """
        name = name or (self.name+':as:Keyspace')
        k = type('dynamicKeyspace',(Keyspace,),{})(self,name=name)
        k.__dict__ = self.__dict__ #copy.copy(self.__dict__)
        return k

    def shutdown(self):
        """ Memory.shutdown effects persistence whenever it is turned on
            TODO: proxy to TSpace shutdown?
        """
        #self.save()
        report("Shutting down Memory.")

    def save(self):
        """ """
        report('persisting memory to', self.filename)
        PersistenceMixin.save(self, self.filename)
        report('persisted memory to', self.filename)

    def __getstate__(self):
        """ typically owner is an agent.. can't serialize those yet. """
        tmp = self.__dict__
        tmp.pop('owner',None)
        return tmp

    def get_many(self, pattern):
        """ revisit this.. probably undermining the underlying optimization """
        out = []
        while True:
            try:
                out.append(self.get(pattern, remove=True))
            except KeyError:
                break
        return out

    #@cache these
    def filter(self, *tests, **kargs):
        """
        """
        remove = kargs.pop('remove', False)
        out    = tuple()
        for item in iter(Memory.values(self, safe=True)):
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
        """ values can be stale.. safe ensures they are
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

    def get(self, *args, **kargs):
        """ """
        #print 'get', args, kargs
        return TSpace.get(self, *args, **kargs)

    def add(self, *args, **kargs):
        """ """
        #print 'added', args, kargs
        return TSpace.add(self, *args, **kargs)

class DefaultKeyMapper(object):
    """ The trivial protocol for mapping a keyspace onto a tuplespace
    """
    def tuple2key(self,t):
        """ covert a tuple to a key """
        return t[0]

    def tuple2value(self, t):
        """ convert a tuple to a value """
        return t and t[1:][0] # destructive! chops off cdr

    def __setitem__(self, key, value):
        """ dictionary compatibility """
        #del self[key]
        self.__delitem__(key)
        #if key in self.keys():
            # enforce the rule by pruning, then add
        #    old_ones = self.filter(lambda t: self.tuple2key(t)==key, remove=True)
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        if isinstance(value,list):
            value = tuple(value)
        self.add( (key, value) )

    def __delitem__(self, key):
        """ dictionary compatibility """
        if key in self.keys():
            old_ones = self.filter(lambda t: self.tuple2key(t)==key, remove=True)

class NotFound(object): pass

class Keyspace(Memory, DefaultKeyMapper):
    """ Thin wrapper around <Memory> to make it look like a dictionary
    """
    def __contains__(self,other):
        return other in self.keys()

    def public_keys(self):
        """ like _keys(), only respects privacy for _ and __
        """
        FORBIDDEN_PREFIXES = '_ __'.split()
        return [ k for k in self._keys() if not any( map(k.startswith, FORBIDDEN_PREFIXES) ) ]
    keys = public_keys

    def __getitem__(self, key):
        """ TODO: is this tailored too much for the PostOffice, or is it sufficiently generic?
            TODO: transparent encryption, serialization, perspective warping, etc
        """
        pattern = (key, object)
        res = self.many( pattern, sys.maxint)
        if len(res) not in [0, 1]:
            raise TypeError("Not really a keyspace then is it?")
        if len(res)==0:
            return NotFound
        else:
            colid, match = res[0]
            return self.tuple2value(match)

    def __contains__(self,other):
        """ dictionary compatibility """
        return other in self.keys()

    def _keys(self):
        """ dictionary compatibility

            1) compute keys from tuplespace
            2) de-dupe the keys
        """
        tspace_values = Memory.values(self, safe=True)
        tspace_keys = [ self.tuple2key(x) for x in tspace_values ]
        return list(set(tspace_keys))

    def __iter__(self):
        """ dictionary compatibility """
        return iter(self.keys())

    def _tspace_as_dict(self):
        """ instead of rewriting functionality for values() and items()
            they will compute their own results directly from what this
            function returns.  essentially, given the tuplespace that
            our KeySpace is being mapped on to, we need to:

            1) compute the de-duped keys from the tuple space
            2) aggregate for every value-set that uses a given key
            TODO: 3) de-dupe the aggregation?
        """
        #keys    = [ k for k in self.keys() if not k.startswith('__') ]
        keys    = self.public_keys() #[ k for k in self.public_keys() if not k.startswith('__') ]
        results = {}
        for k in keys:
            test      = lambda tpl: self.tuple2key(tpl)==k
            value_set = Memory.filter(self, test)
            aggregate = tuple()
            for same_key, this_val in value_set:
                try:
                    aggregate += this_val
                except TypeError:
                    if aggregate:
                        raise
                    else:
                        aggregate=(this_val,)
            results[k] = aggregate
        return results


    def values(self,**kargs):
        """ dictionary compatibility """
        return self._tspace_as_dict().values()

    def items(self):
        """ dictionary compatibility """
        return self._tspace_as_dict().items()
