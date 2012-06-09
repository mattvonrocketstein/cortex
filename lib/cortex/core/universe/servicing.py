"""
"""
import inspect
import types

from cortex.core.util import report

from cortex.core.util import get_mod
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
        def handle_string(service):
            # handle dotpaths
            if "." in service:
                service = service.split('.')
                if len(service) == 2:
                    mod_name, class_name = service

                    namespace = get_mod(mod_name)

                    if class_name in namespace:
                        obj = namespace[class_name]
                        return self.start_service(obj, **kargs)
                else:
                    raise Exception,'will not interpret that dotpath yet'

            # just one word.. where/what could it be?
            else:
                errors = []
                mod_name = service

                ## Attempt to discover a module in cortex.services
                try: mod = get_mod(mod_name)
                except (AttributeError, ImportError), e:

                    ## Log that we were not able to discover a module
                    error = "Failed to get module '{mod}' to load service.".format(mod=mod_name)
                    error = [error, dict(exception=e)]
                    errors.append(error)
                    report(errors)
                    ## Attempt discovery by asking Service's who actually subclasses him
                    subclasses = Service.subclasses(deep=True, dictionary=True, normalize=True)
                    if mod_name.lower() in subclasses:
                        kls = subclasses[mod_name.lower()]
                        return self.start_service(kls, **kargs)
                    else:
                        ## Log that we were not able to discover a subclass
                        error = "Failed to find subclass named {mod}".format(mod=mod_name)
                        error = [error,{}]
                        errors.append(error)
                    mod = {}

                if errors:
                    [self.fault(*err) for err in errors ]

                ret_vals = []
                for name, val in mod.items():
                    if inspect.isclass(val):
                        if not val==Service and issubclass(val, Service):
                            #report('discovered service in ' + mod_name)
                            if not getattr(val, 'do_not_discover', False):
                                # THUNK
                                ret_vals.append(self.start_service(val, ask=False, **kargs))
                return ret_vals

        if isinstance(service, types.StringTypes):
            handle_string(service)
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
