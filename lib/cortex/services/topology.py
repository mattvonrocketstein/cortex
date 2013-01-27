""" cortex.services.topology
"""

from cortex.mixins.topology import TopologyMixin as _TopologyMixin

class TopologyMixin(_TopologyMixin):
    def children(self):
        """ designed to work with manager-mixin """
        children_names = [ name for name in self ]
        children = [self[name].obj for name in children_names]
        return super(TopologyMixin, self).children() + children
