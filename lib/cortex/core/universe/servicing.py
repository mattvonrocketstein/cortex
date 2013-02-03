""" cortex.core.universe.servicing

    This file contains the aspects of the universe
    which deal with finding and loading services.
"""
'''
PEAK-RULES==0.5a1.dev
TODO: multimethods.

>>> @abstract()
... def pprint(ob):
...     """A pretty-printing generic function"""
>>> @when(pprint, (list,))
... def pprint_list(ob):
...     print "pretty-printing a list"
>>> @when(pprint, "isinstance(ob,list) and len(ob)>50")
... def pprint_long_list(ob):
...     print "pretty-printing a long list"
>>> pprint([1,2,3])
pretty-printing a list
>>> pprint([42]*1000)
pretty-printing a long list
'''
import os, sys
import inspect
from types import StringTypes, ModuleType

from cortex.core.util import namedAny
from cortex.core.util import report
from cortex.services import Service
from peak.rules import abstract, when, around, before, after

is_string = lambda s: isinstance(s,StringTypes)
is_dotpath = lambda s: is_string(s) and '.' in s
is_fpath = lambda s: is_string(s) and os.path.sep in s

class ServiceAspect(object):
    def loadAgent(self, arg1):
        pass

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

    @abstract
    def loadService(self, service, **kargs):
        """ load a service """

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
            result = self._load_service_from_word(mod_name)
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
          ("is_string(service) and "
           "not is_dotpath(service) and "
           "not is_fpath(service) and "
           "len(service.split())==1"))
    def loadService(self, service, **kargs):
            return self._load_service_from_word(service, **kargs)

    def start_service(self, obj, ask=False, **kargs):
        """ TODO: bad name?  this is a load() style command,
            i don't think it really starts look back at
            manage implementation specifics
        """
        def service_is_abstract(kls):
            opts = getattr(kls, 'Meta', None)
            return bool(getattr(opts, 'abstract', False))
        if service_is_abstract(obj):
            report('refusing to start an abstract service:', obj)
            return
            #fixme: call a fault here=, cant shutdown the threads cleanly.
            #self.fault('refusing to start an abstract service:', obj)
        else:
            kargs.update(dict(universe=self))
            return self.services.manage(kls = obj,
                                        kls_kargs = kargs,
                                        name=obj.__name__.lower())


    def _load_service_from_word(self, service, **kargs):
        """ inside this method, 'service' is something that
            is just one word.. where/what could it be?
        """
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
                    result = self.start_service(val, ask=False, **kargs)
                    ret_vals.append(result) # THUNK
        return ret_vals
