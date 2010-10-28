""" cortex.core.node
"""

import os

from cortex.core.common import NodeError
from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin

class Node(object, AutonomyMixin, PerspectiveMixin):
    """
    """
    def __init__(self, host=None, instance=None, universe=None,
                 name=None, resource_description=None):
        """
        """
        self.universe = universe
        self.host = host
        self.name = name
        self.instance = instance
        self.resource_description = resource_description
        if hasattr(self,'_post_init'):
            self._post_init()

    def __render_resource_description(self):
        """ """
        return str(self.resource_description)

    def __str__(self):
        """ """
        host = str(self.host)
        instance = str(self.instance)
        resource_descr = self.__render_resource_description()
        return "<"+self.name+" Node@" + host + "::" + instance + " " + resource_descr + ">"

    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]

    def play(self):
        """ CONVENTION:
              play should always return something similar to a derred.
              this is a representation of <self> where <self> has
              fundamentally been *invoked* already and is waiting
              for the universal main loop to begin.

            NOTE: overrides AutonomyMixin.play
        """
        super(Node,self).play()
        for item in self.resource_description.items():
            print '\tevaluating resource:',item
        return self
