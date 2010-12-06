""" cortex.store.tuplespace
"""

from lindypy.TupleSpace import TSpace
from lindypy.TupleSpace import Client, tuplespace

from cortex.core.util import report
from cortex.store.mixins import SubspaceMixin

class CortexTSpace(TSpace, SubspaceMixin):
    """ A thin wrapper around lindypy's tuplespace.

          Everything should be pretty backwards compatible except
          for subspace-functionality (see SubspaceMixin) and the new
          instance method <filter>

    """

    ### Begin overrides from lindy ###
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
        return TSpace.add(self, *args, **kargs)

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

    ### Begin new functionality   ###
    def filter(self, *tests, **kargs):
        """ TODO: cache this?
        """
        remove = kargs.pop('remove', False)
        out    = tuple()
        for item in iter(self.values(safe=True)):
            passes = True
            for test in tests:
                if not hasattr(test,'__call__'):
                    passes = False
                elif not test(item):
                    passes = False
            if passes:
                out += (item,)
                if remove:
                    self.get(item, remove=remove)
        return out
