""" cortex.core.node
"""

import os

from cortex.core.common import NodeError
from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.data import DEFAULT_HOST
from cortex.core.util import report
from cortex.core.mixins import MobileCodeMixin

class Node(MobileCodeMixin, AutonomyMixin, PerspectiveMixin):
    """
        TODO: move selfhostingtuplebus and FOL-KB into node proper
    """
    def __init__(self, host=None, universe=None, name=None, **kargs):
        """
        """
        self.universe = universe
        self.host = host or DEFAULT_HOST
        self.name = name

        # pass the remainder of the kargs to _post_init for subclassers
        if hasattr(self,'_post_init'):
            self._post_init(**kargs)

    def asdf__str__(self):
        """ """
        nayme=self.name
        names = dict(nayme     = nayme,
                     parent   = self.__class__.__bases__[0].__name__,
                     host     = str(self.host),
                     instance = str(self.cortex_instance),)
        return "<{nayme}-{parent}@{host}::{instance}>".format(**names)

    def stop(self):
        #report("node::stopping")
        super(Node, self).stop()

    def play(self):
        """ CONVENTION:
              play should always return something similar to a derred.
              this is a representation of <self> where <self> has
              fundamentally been *invoked* already and is waiting
              for the universal main loop to begin.

            NOTE: overrides AutonomyMixin.play
        """
        super(Node, self).play()
        return self
