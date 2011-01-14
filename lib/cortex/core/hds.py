#!/usr/bin/env python
""" cortex.core.hds: hierarchical data structure pattern

      adapted from:  Recipe 286150: Hierarchical data objects (Python) by Uwe Schmitt
                     ActiveState Code (http://code.activestate.com/recipes/286150/)

"""


import pickle

# Reserved names for dictionary compatibility
FORBIDDEN = 'as_dictionary keys values items'.split()

class HierarchicalData(object):

    """
        organizes hierarchical data as a tree.
        for convenience inner nodes need not be constructed
        explicitly. see examples below.
    """

    def __init__(self):
        # self._d stores subtrees
        self._d = {}

    def as_dictionary(self):
        return dict( [ [x,self._getLeaves()[x]] for x in self._getLeaves().keys() \
                       if x not in FORBIDDEN])
    def keys(self): return self.as_dictionary().keys()
    def values(self): return self.as_dictionary().values()
    def items(self): return self.as_dictionary().items()

    def __getattr__(self, name):
        # only attributes not starting with "_" are organinzed
        # in the tree

        if (name not in FORBIDDEN) and (not name.startswith("_")):
            return self._d.setdefault(name, HierarchicalData())
        raise AttributeError("object %r has no attribute %s" % (self, name))

    def __getstate__(self):
        # for pickling
        return self._d, self._attributes()

    def __setstate__(self, tp):
        # for unpickling
        d,l = tp
        self._d = d
        for name,obj in l: setattr(self, name, obj)

    def _attributes(self):
        # return 'leaves' of the data tree
        return [(s, getattr(self, s)) for s in dir(self) if not s.startswith("_") ]

    def _getLeaves(self, prefix=""):
        # getLeaves tree, starting with self
        # prefix stores name of tree node above
        prefix = prefix and prefix + "."
        rv = {}
        atl = self._d.keys()
        for at in atl:
            ob = getattr(self, at)
            trv = ob._getLeaves(prefix+at)
            rv.update(trv)
        for at, ob in self._attributes():
            rv[prefix+at] = ob
        return rv

    def __str__(self):
        # easy to read string representation of data
        rl = []
        for k,v in self._getLeaves().items():
            rl.append("%s = %s" %  (k,v))
        return "  "+"\n  ".join(rl)


def getLeaves(ob, pre=""):
    """ getLeavess tree, returns dictionary mapping
        paths from root to leafs to value of leafs
    """
    return ob._getLeaves(pre)

# Shortcuts
HDS = HierarchicalData
hds = HierarchicalData
