""" cortex.core.universe.servicing

    aspects of the universe dealing with how to find and load services
"""
import os, sys
import inspect
import types

from cortex.core.util import report

from cortex.core.util import get_mod as _get_mod
from cortex.services import Service

class ServiceAspect(object):
    def loadServices(self, services=[]):
        """ """
        for s in services:
            if isinstance(s,(list,tuple)):
                s, kargs = s
            else:
                kargs = {}
            try: self.loadService(s,**kargs)
            except (SyntaxError, ImportError), e:
                error   = "Failed to get module {mod} to load service.".format(mod=s)
                context = dict(exception=e)
                self.fault(error, context)

    def loadService(self, service, **kargs):
        """ """
        if isinstance(service, types.StringTypes):
            self._load_service_from_string(service, **kargs)
        # Not a string? let's hope it's already a service-like thing
        else:
            return self.start_service(service, **kargs)


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
        else:
            kargs.update(dict(universe=self))
            return self.services.manage(kls = obj,
                                        kls_kargs = kargs,
                                        name=obj.__name__.lower())

    def _load_service_from_dotpath(self, service, **kargs):
        """ """
        service = service.split('.')
        if len(service) == 2:
            mod_name, class_name = service
            namespace = _get_mod(mod_name)
            if class_name in namespace:
                obj = namespace[class_name]
                return self.start_service(obj, **kargs)
        else:
            raise Exception, 'will not interpret that dotpath yet'

    def get_mod(self, mod_name):
        """ """
        try:
            return _get_mod(mod_name), []
        except (AttributeError, ImportError), e:
            return None, [e]

    def _get_mod_from_wd(self, mod_name):
        """ """
        try:
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())
            exec 'import '+mod_name
            mod = eval(mod_name)
            return mod, []
        except (AttributeError, ImportError), e:
            return None, [e]

    def _load_service_from_string(self, service, **kargs):
        """ """
        if "." in service: # handle dotpaths
            return self._load_service_from_dotpath(service, **kargs)
        else:
            return self._load_service_from_word(service, **kargs)

    def _load_service_from_word(self, service, **kargs):
        """ inside this method, 'service' is something that
            is just one word.. where/what could it be?
        """
        errors   = []
        mod_name = service

        default               = lambda mod_name: [],{}
        module_search_methods = [ self.get_mod, self._get_mod_from_wd, default ]
        for search_method in module_search_methods:
            mod, _errs = search_method(mod_name)
            errors    += [ _errs ]
            if mod:
                # found a module?  reset the errors to empty
                # and start and exit the loop immediately
                errors = []
                break

        if isinstance(mod, types.ModuleType):
            mod = dict([ [x, getattr(mod, x)] for x in dir(mod) ])

        ret_vals = []
        for name, val in mod.items():
            if inspect.isclass(val):
                if all([ not val == Service, issubclass(val, Service),
                         not getattr(val, 'do_not_discover', False) ]):
                    result = self.start_service(val, ask=False, **kargs)
                    ret_vals.append(result) # THUNK
        return ret_vals
