""" cortex.store.transforms

      Conversion rules for tuple-space <--> Keyspace
"""
class DefaultKeyMapper(object):
    """ The trivial protocol for mapping a tuplespace to a keyspace
    """
    def tuple2key(self,t):
        """ """
        return t[0]

    def tuple2value(self, t):
        """ """
        return t and t[1:][0]

    def __setitem__(self, key, value):
        """ dictionary compatibility """
        if key in self.keys():
            # enforce the rule by pruning, then add
            old_ones = self.filter(lambda t: self.tuple2key(t)==key, remove=True)
        self.add( (key, value) )
