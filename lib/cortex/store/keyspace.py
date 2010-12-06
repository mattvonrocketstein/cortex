""" cortex.store.keyspace
"""

from cortex.store.ground import Memory
from cortex.store.transforms import DefaultKeyMapper

class Keyspace(Memory, DefaultKeyMapper):
    """ Thin wrapper around <Memory> to make it look like a dictionary
    """
    #def __init__(self, *

    def __contains__(self,other):
        return other in self.keys()

    def public_keys(self):
        """ like self.keys(), only respects privacy for _ and __
        """
        FORBIDDEN_PREFIXES = '_ __'.split()
        return [ k for k in self.keys() if not any( map(k.startswith, FORBIDDEN_PREFIXES) ) ]

    def __getitem__(self, key):
        """ TODO: is this tailored too much for the PostOffice, or is it sufficiently generic?
            TODO: transparent encryption, serialization, perspective warping?
        """
        matching_tuples = self.filter(lambda tpl: self.tuple2key(tpl)==key)
        #assert len(matching_tuples)<2,"Found duplicate matching tuples.. not really a keyspace then, is it?"
        if matching_tuples:
            first_match = matching_tuples[0]
            return self.tuple2value(first_match)
        return NOT_FOUND_T

    def subspace(self, name):
        """ return a nested keyspace with name <name> """
        NIY
    def asdkeys(self):
        if self.subspace_of:
            return self.subspace_of[self.name]

    def __contains__(self,other):
        """ dictionary compatibility """
        return other in self.keys()

    def keys(self):
        """ dictionary compatibility: (almost)

              NOTE: this list may contain duplicates.. this is intentional
        """
        return [ self.tuple2key(x) for x in self.values() ]

    def __iter__(self):
        """ dictionary compatibility """
        return iter(self.keys())

    def items(self):
        """ dictionary compatibility: (almost)

                NOTE: this list may contain duplicates.. this is intentional
        """
        return [ [ self.tuple2key(x), self.tuple2value(x) ] for x in self.values() ]

