""" cortex.core.universe

      The universe is an abstraction intended to unify the representation
      of aspects of the interpretter, the operating system, the "mainloop",
      the process, and the cortex runtime.  It should effectively be a
      singleton-- one per process.
"""
import types
import inspect
import os, sys
import platform, pprint, StringIO
from multiprocessing import Process

from twisted.internet import reactor

from cortex.core.hds import HDS
from cortex.core.util import get_mod
from cortex.core.reloading import AutoReloader
from cortex.core.parsing import Nodeconf
from cortex.core.util import report
from cortex.mixins import AutonomyMixin, PerspectiveMixin,ControllableMixin
from cortex.mixins import PersistenceMixin
from cortex.core.peer import PEERS
from cortex.services import Service, SERVICES
from cortex.core.agent import AGENTS
from cortex.mixins import OSMixin, PIDMixin
from cortex.core.notation import UniverseNotation
from cortex.mixins import FaultTolerant


class ReactorAspect(object):
    reactor       = reactor
    callLater     = reactor.callLater
    listenTCP     = reactor.listenTCP
    getThreadPool = reactor.getThreadPool

    def callInProcess(self, target, args=tuple(),
                      name='DefaultProcessName', delay=1, **kargs):
        """ """
        p = Process(target=target, args=args, name=name, **kargs)
        def start():
            self.procs.append(p)
            report('starting process "{0}" ({1} total)'.format(p.name, len(self.procs)))
            p.start()
        def finish():
            p.join()
            self.procs.remove(p)
            report('finished with process "{0}" ({1} left)'.format(p.name,len(self.procs)))
        def go():
            start()
            finish()
        self.callLater(delay, go)

class __Universe__(AutoReloader, UniverseNotation,
                   OSMixin, PIDMixin, ReactorAspect,
                   ControllableMixin, AutonomyMixin,
                   PerspectiveMixin, PersistenceMixin,
                   FaultTolerant):
    """
        TODO: clones,processes = CloneManager(), ProcessManager()
    """
    agents, services = AGENTS, SERVICES

    peers         = PEERS
    nodeconf_file = u''
    config        = HDS()
    parent = None # agent.__init__ never called?

    def read_nodeconf(self):
        """ iterator that returns decoded json entries from self.nodeconf_file
        """
        nodeconf_err = 'Universe.nodeconf_file tests false or is not set.'
        assert hasattr(self, 'nodeconf_file') and self.nodeconf_file, nodeconf_err
        jsons = Nodeconf(self.nodeconf_file).parse()
        return jsons

    @property
    def Nodes(self):
        """ nodes: static definition """
        blammo = getattr(self, '_use_nodeconf', self.read_nodeconf)
        return blammo() if callable(blammo) else blammo

    @classmethod
    def set_nodes(self, val):
        """ method to overwrite the property above.  might seem weird, but
            the universe is a singleton so it's not really that strange.
            why would you use this?  maybe you're generating it dynamically
            instead of from a file.  or, if you're initializing the universe
            completely via the API, maybe it would be useful afterwards to
            call something like Universe.set_nodes([]) to use a nil config
            w/o saving such a trivial thing to a file.
        """
        self.Nodes = val

    def load(self):
        """ call load for all embedded managers """
        self.services.load()
        self.agents.load()

    def play(self):
        """ entry point.  this guy does not return """
        #report("Universe.play!")
        self.decide_name()
        self.started = True
        from cortex.core import api as API
        from cortex.core.api import publish
        _api = publish()

        def parse_error(error, instruction, args, kargs, api=_api):
            api_header = "Cortex-API @ {H}://{F}"
            api_header = api_header.format(F=API,
                                           H=platform.node(),)
            fhandle    = StringIO.StringIO();
            pprint.pprint(api, fhandle)
            opts   = dict(api=api_header, instruction=instruction,args=args,kargs=kargs)
            header = "ParseError: {E}:".format(E=error)
            body   = ("instruction = {instruction}\n"
                      "args        = {args}\n"
                      "kargs       = {kargs}\n"
                      "with api    = {api}\n")
            error  = (header + body).format(**opts)
            report(error)
            sys.exit()

        def get_handler(instruction):
            """ grab an item named "instruction" from the api """
            return _api.get(instruction)

        # Interprets all the instructions in the nodeconf
        for node in self.Nodes:
           original = node
           instruction, args = node[0], node[1:]
           #report("parsing node", node)
           if len(args)==1:
               kargs = {}
           else:
               args = args[:-1]
               kargs = (args and args[-1]) or {}

           handler = get_handler(instruction)
           if not handler:
               parse_error("No instruction handler!", instruction, args, kargs)
           handler(*args, **kargs)

        # is this working?
        for name, kls, kls_kargs in self.agents._pending:
            kls_kargs.update( { 'universe' : self } )

        # Call load for all embedded managers
        self.load()

        # Setup threadpool
        self.threadpool = self.getThreadPool()

        # Main loop
        self.reactor.run()

    def children(self):
        """ """
        return self.agents.children() + self.services.children()

    def sleep(self):
        """
            TODO: send a better signal and use os/pid mixins.
        """
        self.stop()
        for pid in self.pids['children']:
            os.system('kill -KILL ' + str(pid))
        # self.persist()

    def halt(self):
        """ override from ControllableMixin

            sometimes the universe needs to have it's shutdown triggered by another
            agent, for example when the terminal agent received control-D.  in those
            circumstances, until there is a signal for this, the caller should
            *always* use halt instead of 'stop'.
        """
        #from cortex.core.util import getcaller
        #report('shutting down at the request of:'); print getcaller()
        return self.reactor.callFromThread(self.stop)

    def stop(self):
        """ override autonomy """
        if not self.started:
            return
        self.started = False
        stopped = []

        def failure_stopping_agent(service, e):
            err_msg = ('Squashed exception stopping agent'
                       ' "' + str(service) + '".  '
                       'Original Exception follows')

            report(err_msg)
            report(str(e))
            raise e

        ## stop any other agents
        for agent in set(self.agents.values() + self.services.values()):
            try:
                agent.stop()
                stopped.append(agent)
            except Exception,e:
                failure_stopping_agent(agent, e)

        # we have to check first,
        # maybe bootstrap didn't even get this far
        if hasattr(self,'threadpool'):
            self.threadpool.stop()

        for thr in self.threads:
            thr._Thread__stop()

        import twisted
        try:
            self.reactor.stop()
        except twisted.internet.error.ReactorNotRunning:
            pass
        report("Stopped: ", [x for x in stopped] )

    def decide_name(self):
        """ most agents get a name, but the universe computes hers """
        name_args = dict( alfa    = str(id(self)),
                          bravo   = getattr(self,'bravo', ''),
                          charlie = getattr(self,'charlie',''),
                          delta   = self.hostname,)
        name = 'Universe({alfa})[{bravo}:{charlie}]@{delta}'.format(**name_args)
        self.name    = name
        return name

    def loadServices(self, services=[]):
        """ """
        for s in services:
            if isinstance(s,(list,tuple)):
                s, kargs = s
            else:
                kargs = {}
            self.loadService(s,**kargs)

    def loadService(self, service, **kargs):
        """ """
        def handle_string(service):
            # handle dotpaths
            if "." in service:
                service = service.split('.')
                if len(service) == 2:
                    mod_name, class_name = service

                    try: namespace = get_mod(mod_name)
                    except ImportError, e:
                        error   = "Failed to get module {mod} to load service.".format(mod=mod_name)
                        context = dict(exception=e)
                        self.fault(error, context)
                    else:
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
        if ask:
            raise Exception,'obsolete'
        else:
            kargs.update(dict(universe=self))
            return self.services.manage(kls = obj,
                                        kls_kargs = kargs,
                                        name=obj.__name__.lower())

# A cheap singleton
Universe = __Universe__()

# Set all the back-refs
AGENTS.universe   = Universe
PEERS.universe    = Universe
SERVICES.universe = Universe
