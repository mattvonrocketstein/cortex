""" cortex.core.node
"""

import os

from cortex.core.util import report
from cortex.core.metaclasses import META1
from cortex.core.common import AgentError
from cortex.core.data import NOOP, LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from cortex.core.data import DEFAULT_HOST
from cortex.mixins import MobileCodeMixin
from cortex.core.manager import Manager

class AgentManager(Manager):
    """ """
    # TODO: not enforced..
    load_first = ['ServiceManager']

    # Class specifying how the objects in this
    #  container will be represented
    asset_class = HierarchicalData

    class AgentPrerequisiteNotMet(Exception):
        """ Move along, nothing to see here """

    def __init__(self, universe=None, **kargs):
        """ """
        super(AgentManager,self).__init__(**kargs)
        self.universe   = universe
        self.registry   = {}

        # TODO: when in doubt, autoproxy to..
        self.generic_store = HierarchicalWrapper('obj')

    def items(self):
        """ dictionary compatability """
        return [[var, val.obj] for var,val in Manager.items(self)]

    def stop_all(self):
        """ stop all services this manager knows about """
        [ s.stop() for s in self ]

    def pre_manage(self, name=None, kls=None, **kls_kargs):
        """ make an educated guess whenever 'name' is not given
        """
        if 'name' not in kls_kargs:
            kls_kargs['name'] = name
        return name, kls, kls_kargs

    def pre_load_obj(self, kls=None, **kls_kargs):
        """ pre_load_obj hook:
        """
        assert self.universe, 'universe is broken!'

        # enforce requirements (NOTE: servicemanager will want to undo this)
        required_services = getattr(kls, 'requires_services',[])
        for service_name in required_services:
                if (self.universe|service_name) is None:
                    fmt = dict(t1=kls.__name__, t2=service_name)
                    err = 'Service-requirement not met for Agent({t1}): "{t2}"'.format(**fmt)
                    raise AgentPrerequisiteNotMet, err

        return super(AgentManager,self).pre_load_obj(kls=kls, **kls_kargs)

    def post_load_obj(self, obj):
        """ post_load_obj hook:
        """
        return obj.play()

    def pre_registration(self, name, **metadata):
        """ pre_registration hook """
        return name, metadata

    def post_registration(self, asset):
        """ pre_registration hook """
        report( asset.obj )

class Agent(MobileCodeMixin, AutonomyMixin, PerspectiveMixin):
    """
        CONVENTION: __init__ always passes unconsumed kargs to _post_init()

        TODO: move SelfHostingTupleBus and FOL-KB into agents-proper
        TODO: Make mixin classes work with __add__

    """
    __metaclass__ = META1 # a metaclass that tracks all the subclasses for this class
    _post_init    = NOOP
    name          = 'default-name'


    def __init__(self, host=None, universe=None, name=None, **kargs):
        """
            TODO: "host" is bad.  use a better address formalism instead.
        """
        self.universe = universe
        self.host     = host or DEFAULT_HOST
        self.name     = name
        self._post_init(**kargs)

    def stop(self):
        """ autonomy override:
            by convention, usage of <stop> shows that this agents
            is stopping himself.  (if other agents are able to stop
            this agent, it is more appropriate to use <halt> or
            <shutdown> instead.)
        """
        super(Agent, self).stop()

    def iterate(self):
        """ Convention:
              <iterate> is typically called by <play>, but
              whereas <play> is (under normal circumstances)
              only called once, <iterate> may be called several
              times.
        """

    def play(self):
        """ Convention:
              <play> should always return something similar to a deferred.
              This is a representation of <self> where <self> has
              fundamentally been *invoked* already and is waiting
              for the universal main loop to begin.

            NOTE: overrides AutonomyMixin.play
        """
        if hasattr(self, 'setup'):
            self.setup()
        super(Agent, self).play()
        self.universe.reactor.callLater(1,self.iterate)
        return self

Node    = Agent         # Alias
AGENTS = AgentManager() # A cheap singleton
