""" cortex.core.agent
"""

import inspect

from cortex.core.util import report, uniq

from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from cortex.core.manager import Manager

class AgentPrerequisiteNotMet(Exception):
    """ Move along, nothing to see here """

class AgentManager(Manager):
    """ """
    AgentPrerequisiteNotMet = AgentPrerequisiteNotMet

    @classmethod
    def choose_dynamic_name(kls):
        """ when __call__ happens, if name is
            not passed, then this will be used.
        """
        from cortex.core.util import getcaller
        caller_info = getcaller(3)
        func_name = caller_info.get('func_name')
        return "{parent}_{u}".format(parent=func_name,u=uniq())


    load_first = ['ServiceManager'] # TODO: not enforced..

    # Class specifying how the objects in this
    #  container will be represented
    asset_class = HierarchicalData

    def __mod__(self, other):
        """ AgentManager % kls:

              partitions the registry by type
        """
        assert inspect.isclass(other),str(NotImplemented)
        out = {}
        for key,agent in self.as_dict.items():
            if isinstance(agent, other): out[key]=agent
        return out

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

    def flush(self):
        """ TODO: test this """
        self.stop_all()
        self.registry = {}

    def stop_all(self):
        """ stop all services this manager knows about """
        [ item.obj.stop() for item in self.registry.values() ]

    def pre_manage(self, name=None, kls=None, **kls_kargs):
        """ make an educated guess whenever 'name' is not given """
        if 'name' not in kls_kargs:
            kls_kargs['name'] = name
        return name, kls, kls_kargs

    def pre_load_obj(self, kls=None, **kls_kargs):
        """ pre_load_obj hook: """
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
        """ post_load_obj hook: """
        obj.parents += [self]
        return obj.play()

    def pre_registration(self, name, **metadata):
        """ pre_registration hook """
        return name, metadata

    @property
    def agents(self): return self.registry

AGENTS = AgentManager() # A cheap singleton
