""" cortex.core.node
"""

import os

from cortex.core.common import AgentError
from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from cortex.core.data import DEFAULT_HOST
from cortex.mixins import MobileCodeMixin
from cortex.core.manager import Manager
from cortex.core.util import report
from cortex.mixins._os import OSMixin

class AgentPrerequisiteNotMet(Exception):
    """ Move along, nothing to see here """

class CloneManager(Manager):
    from cortex.core.hds import HDS

    class Clone(HDS):
        def __repr__(self):
            return self.label

        @property
        def pids(self):
            """ HACK """
            from cortex.core.universe import Universe
            return Universe.pids_for_pattern(self.label)

        def kill(self):
            from cortex.core.universe import Universe
            return [p.kill() for p in Universe.procs_for_pattern(self.label)]

    asset_class=Clone

class AgentManager(Manager):
    """
    """

    load_first = ['ServiceManager']     # TODO: not enforced..

    # Class specifying how the objects in this
    #  container will be represented
    asset_class = HierarchicalData

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

# A cheap singleton
AGENTS = AgentManager()
CLONES = CloneManager()

class Agent(MobileCodeMixin, AutonomyMixin, PerspectiveMixin):
    """
        TODO: move SelfHostingTupleBus and FOL-KB into agents-proper
    """
    name = 'default-name'

    def __init__(self, host=None, universe=None, name=None, **kargs):
        """
        """
        self.universe = universe
        self.host     = host or DEFAULT_HOST
        self.name     = name

        # pass the remainder of the kargs to _post_init for subclassers
        if hasattr(self, '_post_init'):
            self._post_init(**kargs)

    def stop(self):
        """ Convention:
              <stop> should..
        """
        #report("node::stopping")
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

Node = Agent
