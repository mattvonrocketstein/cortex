""" cortex.core.universe.servicing

    This file contains the aspects of the universe
    which deal with finding and loading services.
"""
import os, sys
import inspect
from types import StringTypes, ModuleType

from cortex.core.util import namedAny
from cortex.core.util import report
from cortex.services import Service
from cortex.agents import Agent

from peak.rules import abstract, when, around, before, after

is_string = lambda s: isinstance(s,StringTypes)
is_dotpath = lambda s: is_string(s) and '.' in s
is_fpath = lambda s: is_string(s) and os.path.sep in s

def service_is_abstract(kls):
    opts = getattr(kls, 'Meta', None)
    return bool(getattr(opts, 'abstract', False))

class ServiceAspect(object):

    @abstract
    def loadAgent(self, agent, **kargs): pass
    @abstract
    def loadService(self, service, **kargs): pass


    # TODO: bad names?  this is sort of a load() style command
    @abstract
    def start_service(self, obj, **kargs): pass
    @abstract
    def start_agent(self, obj, **kargs): pass

    @when(loadAgent, 'is_dotpath(agent)')
    def loadAgent(self, agent, **kargs):
        kls = namedAny(agent)
        if not issubclass(kls, Agent):
            msg = ("There is an error in your configuration file. "
                   'The dotpath given by "{0}" resolves to a {1}, '
                   "but it should be a Agent.")
            msg = msg.format(service_path, type(kls).__name__)
            raise ValueError(msg)
        return self.start_agent(kls, **kargs)

    def loadServices(self, services=[]):
        """ """
        for s in services:
            if isinstance(s, (list, tuple)):
                s, kargs = s
            else:
                kargs = {}
            try: self.loadService(s,**kargs)
            except (SyntaxError, ImportError), e:
                error   = "Failed to get module {mod} to load service.".format(mod=s)
                context = dict(exception=e)
                self.fault(error, context)

    @when(loadService, "not is_string(service)")
    def loadService(self, service, **kargs):
        """ Not a string? let's hope it's already a service-like thing """
        return self.start_service(service, **kargs)

    @when(loadService, "is_fpath(service)")
    def loadService(self, service, **kargs):
        curr     = os.getcwd()
        fpath    = os.path.expanduser(service)
        fpath    = os.path.abspath(os.path.dirname(fpath))
        mod_name = os.path.splitext(os.path.split(service)[-1])[0]
        os.chdir(fpath)
        try:
            #result = self._load_service_from_word(mod_name)
            result = self.loadService(mod_name)
        finally:
            os.chdir(curr)
        return result

    @when(loadService, "is_dotpath(service)")
    def loadService(self, service, **kargs):
        kls = namedAny(service)
        if not issubclass(kls, Service):
            msg = ("There is an error in your configuration file. "
                   'The dotpath given by "{0}" resolves to a {1}, '
                   "but it should be a Service.")
            msg = msg.format(service_path, type(kls).__name__)
            raise ValueError, msg
        return self.start_service(kls, **kargs)

    @when(loadService,
          ("is_string(service) and not is_dotpath(service) and "
           "not is_fpath(service) and len(service.split())==1"))
    def loadService(self, service, **kargs):
        # inside this method, 'service' is something that
        # is just one word.. where/what could it be?
        errors   = []
        mod_name = service

        def default_search(mod_name):
            return ( {}, {} )
        mod = namedAny('cortex.services.{0}'.format(service))
        if not mod:
            raise ValueError("Service not found.. there may be "
                             "an error in your configuration")

        if isinstance(mod, ModuleType):
            mod = dict([ [x, getattr(mod, x)] for x in dir(mod) ])

        ret_vals = []

        for name, val in mod.items():
            if inspect.isclass(val):
                if all([ not val == Service, issubclass(val, Service),
                         not getattr(val, 'do_not_discover', False) ]):
                    result = self.start_service(val, **kargs)
                    ret_vals.append(result) # THUNK
        return ret_vals

    @when(start_service,'service_is_abstract(obj)')
    def start_service(self, obj, **kargs):
        #fixme: call a fault here=, cant shutdown the threads cleanly.
        #self.fault('refusing to start an abstract service:', obj)
        report('refusing to start an abstract service:', obj)

    @when(start_service,'not service_is_abstract(obj)')
    def start_service(self, obj, **kargs):
        kargs.update(__manager=self.services)
        return self.start_agent(obj, **kargs)


    def start_agent(self, obj, **kargs):
        kargs.update(dict(universe=self))
        manager = kargs.pop('__manager', self.agents)
        return manager.manage(kls = obj,
                              kls_kargs = kargs,
                              name=obj.__name__.lower())
