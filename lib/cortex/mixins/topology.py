""" cortex.mixins.topology
"""
class TopologyMixin(object):
    def children(self):
        return []

    @property
    def parent(self):
        """ Warning this might not be an agent! """
        if len(self.parents):
            if len(self.parents)<2: return self.parents[0]
            else: self.fault('ambiguous topology')
        else:
            return None

    @property
    def siblings(self):
        out = [ x for x in self.parent.children() if x!=self ]
        out = dict([ [x.name, x] for x in out ])
        return out
