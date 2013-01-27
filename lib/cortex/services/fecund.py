""" cortex.services.fecund
"""
from collections import defaultdict
from cortex.core.agent.manager import AgentManager
from cortex.services import Service

from .topology import TopologyMixin

class FecundService(TopologyMixin, Service, AgentManager):
    """ FecundService describes a service with children.

        You get mostly the semantics you'd expect.  When the
        parent is start()'ed, the children start, and similarly
        for stop().

        To use, subclassers should define a Meta like this:


           class Meta:
               children = [ChildClass-1, ChildClass-2, .. ]
    """
    class Meta:
        abstract = True

    def __init__(self, *args, **kargs):
        Service.__init__(self, **kargs)
        AgentManager.__init__(self, **kargs)

    def start(self):
        """ """
        ctx = dict(universe=self.universe)
        child_classes = self._opts.children
        for kls in child_classes:
            name = kls.__name__
            kargs = dict(kls=kls, kls_kargs=ctx, name=name)
            self.manage(**kargs)
        self.load()
        Service.start(self)
