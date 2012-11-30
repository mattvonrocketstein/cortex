""" cortex.core.universe.servicing

    This file contains the aspects of the universe
    which deal with finding and loading services.
"""
import os, sys
import inspect
import types

from cortex.core.util import namedAny
from cortex.core.util import report
from cortex.services import Service

class ServiceAspect(object):
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

    def _load_service_from_dotpath(self, service_path, **kargs):
        """ """
        kls = namedAny(service_path)
        if not issubclass(kls, Service):
            msg = ("There is an error in your configuration file. "
                   'The dotpath given by "{0}" resolves to a {1}, '
                   "but it should be a Service.")
            msg = msg.format(service_path, type(kls).__name__)
            raise ValueError, msg
        return self.start_service(obj, **kargs)

    def _load_service_from_string(self, service, **kargs):
        """ """
        if os.path.sep in service:
            return self._load_service_from_fpath(service, **kargs)
        elif "." in service: # handle dotpaths
            return self._load_service_from_dotpath(service, **kargs)
        else:
            return self._load_service_from_word(service, **kargs)

    def _load_service_from_fpath(self, service, **kargs):
        """ """
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
            msg = "Service not found.. there may be an error in your configuration"
            raise ValueError,msg

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
