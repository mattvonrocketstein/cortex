""" cortex.core.node
"""

import os

from cortex.core.common import NodeError
from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from cortex.core.data import DEFAULT_HOST
from cortex.core.mixins import MobileCodeMixin
from cortex.core.manager import Manager
from cortex.core.util import report

class AgentManager(Manager):

    # Class specifying how the objects in this
    #  container will be represented
    asset_class = HierarchicalData
    def __init__(self, *args, **kargs):
        """ """
        self.registry   = {}
        self._pending   = []
        self.boot_order = None

        # TODO: when in doubt, autoproxy to..
        self.generic_store = HierarchicalWrapper('obj')

    def items(self):
        """ dictionary compatability """
        return [[var, val.obj] for var,val in Manager.items(self)]

    def stop_all(self):
        """ stop all services this manager knows about """
        [ s.stop() for s in self ]

    def preprocess_kargs(self, **kls_kargs):
        # shot in the dark..
        if 'name' not in kls_kargs:
            kls_kargs['name'] = name
        return kls_kargs

    def manage(self, name=None, kls=object, kls_kargs={}):
        """ queue up a pile of future assets and the arguments to
            initialize them with.  this pile will be dealt with when
            <load> is called.
        """
        self.preprocess_kargs(**kls_kargs)
        self._pending.append([name, kls, kls_kargs])
        return name

    def resolve_boot_order(self, **kargs):
        """ by default, simply returns the names in
            the order they were registered """
        return [pending[0] for pending in self._pending ]

    def load(self):
        """ if <manage> is used, this should be called after
            all calls to it are finished

            TODO: refactor
        """
        self.boot_order = self.resolve_boot_order()
        report('determined boot order:', self.boot_order)
        for name in self.boot_order:
            for item in self._pending:
                name2, kls, kls_kargs = item
                kls_kargs = kls_kargs or {}
                if name2 == name:
                        self.register(name,
                                      obj        = kls(**kls_kargs).play(),
                                      boot_order = self.boot_order.index(name),
                                      kargs      = kls_kargs)

    def post_registration(self, asset):
        report(asset.obj)

class Node(MobileCodeMixin, AutonomyMixin, PerspectiveMixin):
    """
        TODO: move selfhostingtuplebus and FOL-KB into node proper
    """

    name='default-name'

    def __init__(self, host=None, universe=None, name=None, **kargs):
        """
        """
        self.universe = universe
        self.host = host or DEFAULT_HOST
        self.name = name

        # pass the remainder of the kargs to _post_init for subclassers
        if hasattr(self,'_post_init'):
            self._post_init(**kargs)

    def stop(self):
        """ Convention:
              <stop> should..
        """
        #report("node::stopping")
        super(Node, self).stop()
    def iterate(self):
        report('hi')

    def play(self):
        """ Convention:
              <play> should always return something similar to a deferred.
              this is a representation of <self> where <self> has
              fundamentally been *invoked* already and is waiting
              for the universal main loop to begin.

            NOTE: overrides AutonomyMixin.play
        """
        if hasattr(self, 'setup'):
            self.setup()
        super(Node, self).play()
        self.universe.reactor.callLater(1,self.iterate)
        return self

Agent = Node

class TaskList(Agent):
    """ """
    def _post_init(self, tasks=[]):
        """ """
        self.tasks = tasks

    def start(self):
        """ """
        while self.tasks:
            task = self.tasks.pop()
            task()
