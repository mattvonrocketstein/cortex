""" cortex.core.node
"""

import os

from cortex.core.common import NodeError
from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.data import DEFAULT_HOST
from cortex.core.util import report

class MobileCodeMixin(object):
    """ """
    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]

class Node(object, MobileCodeMixin, AutonomyMixin, PerspectiveMixin):
    """
    """
    def __init__(self, host=None, instance=None, universe=None,
                 name=None, resource_description=None):
        """
        """
        self.universe = universe
        self.host = host or DEFAULT_HOST
        self.name = name
        #self.instance = instance
        self.resource_description = resource_description
        if hasattr(self,'_post_init'):
            self._post_init()

    @property
    def cortex_instance(self):
        return self.universe.instance_dir

    def __str__(self):
        """ """
        nayme=self.name
        names = dict(nayme     = nayme,
                     parent   = self.__class__.__bases__[0].__name__,
                     host     = str(self.host),
                     instance = str(self.instance),)
                     #resource_descr = self.__render_resource_description())
        return "<{nayme}-{parent}@{host}::{instance}>".format(**names)

    def __render_resource_description(self):
        """ OBSOLETE? """
        return str(self.resource_description)

    def stop(self):
        report("node::stopping")
        super(Node,self).stop()

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
