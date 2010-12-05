""" cortex.core.universe

      The universe is an abstraction intended to unify the representation
      of aspects of the interpretter, the operating system, the "mainloop",
      and the cortex runtime.  It should (probably) effectively be a singleton--
      one per process.
"""

# Imports from python core modules
import os, sys
import multiprocessing
import inspect, types
from tempfile import NamedTemporaryFile

# Imports from third-party
import simplejson
from twisted.internet import reactor

# Import Cortex modules
from cortex.core.parsing import Nodeconf
from cortex.util import Memoize, Namespace
from cortex.mixins import OSMixin, PIDMixin
from cortex.core.atoms import AutonomyMixin
from cortex.core.util import report, console
from cortex.core.data import SERVICES_DOTPATH
from cortex.core.atoms import PerspectiveMixin
from cortex.core.atoms import PersistenceMixin
from cortex.core.reloading import AutoReloader
from cortex.core.notation import UniverseNotation

class ServiceLoader:
    """ The only class likely to inherit/mix this in is the Universe """
    def _load_service_from_dotpath(self, dotpath, **kargs):
        """ dispatched to from _load_service_from_string """
        dotpath = dotpath.split('.')
        if len(service) == 2:
            mod_name, class_name = dotpath
            try: namespace = Namespace.from_module(SERVICES_DOTPATH, mod_name, **kargs)
            except ImportError, e:
                #raise e
                report("Failed to get module {mod} to load service.".format(mod=mod_name))
            else:
                namespace = namespace.only_classes()
                if class_name in namespace:
                    obj = namespace[class_name]
                    return self.start_service(obj, **kargs)
        else:
            raise Exception,'will not interpret that dotpath yet'

    def _load_service_from_string(self, mod_name, **kargs):
        """ dispatched to from loadService """

        # handle dotpaths
        if "." in mod_name:
            return self._load_service_from_dotpath(mod_name, **kargs)

        # just one word.. where/what could it be?
        else:
            return self._load_service_from_autodiscover(mod_name, **kargs)

    def _load_service_from_autodiscover(self, mod_name, **kargs):
        """ """

        # try to autodiscover  a module for it
        try:
            namespace = Namespace.from_module(SERVICES_DOTPATH, mod_name,
                                              dictionaries=False)
        except ImportError, e:
            report("Failed to get module '{mod}' to load service.".format(mod=mod_name))
            namespace = Namespace({}, dictionaries=False)

        # Slice up the namespace to get just the things that might be services
        tests     = Namespace.Tests
        namespace = namespace % tests.isclass    # only classes
        namespace = namespace % tests.isservice  # only service classes
        namespace = namespace % tests.concrete   # only concrete service classes

        ret_vals = []
        for name, val in namespace.items():
            #report('discovered service in ' + mod_name)
            if not getattr(val, 'do_not_discover', False):
                ret_vals.append(self.start_service(val, ask=False, **kargs)) # THUNK
        return ret_vals


    def loadService(self, service, **kargs):
        """ """
        # got string?
        if isinstance(service, types.StringTypes):
            return self._load_service_from_string(service,**kargs)

        # not string? let's hope it's already a service-like thing
        else:
            return self.start_service(service, **kargs)


    def start_service(self, kls, ask=False, **kargs):
        """ obj is actually a service_kls?
        """
        kargs.update(dict(universe=self))
        return self.services.manage(kls = kls,
                                    kls_kargs = kargs,
                                    name=kls.__name__.lower())

class __Universe__(AutoReloader, OSMixin, UniverseNotation, ServiceLoader,
                   AutonomyMixin, PerspectiveMixin, PersistenceMixin):
    """
         Reality is that which, when you stop looking, doesn't go away. --PKD
    """
    nodeconf_file = u''
    system_shell  = 'xterm -fg green -bg black -e '
    reactor       = reactor

    # Import Manager singletons
    from cortex.core.peer import PEERS as peers
    from cortex.core.service import SERVICES as services
    from cortex.core.node import AGENTS as agents
    #clones        = CloneManager()
    #processes     = ProcessManager()


    def decide_options(self):
        """ """
        return "--directives=do_not_clone"

    @property
    def tumbler(self):
        from xanalogica.tumbler import Tumbler
        return

    def read_nodeconf(self):
        """ iterator that returns decoded json entries from self.nodeconf_file
        """
        nodeconf_err = 'Universe.nodeconf_file tests false or is not set.'
        assert hasattr(self, 'nodeconf_file') and self.nodeconf_file, nodeconf_err
        jsons = Nodeconf(self.nodeconf_file).parse()
        return jsons

    def play(self):
        """
            Post-conditions:
        """
        report("Universe.play!")
        self.decide_name()
        self.started = True

        def get_handler(instruction):
            """ grab an item named "instruction" from the api """
            from cortex.core.api import publish
            _api = publish()
            return _api.get(instruction)

        # Interprets all the instructions in the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.read_nodeconf():
            #for node in self.read_nodeconf():
                original = node
                instruction, args = node[0], node[1:]

                report("parsing node",node)
                if len(args)==1:
                    kargs = {}
                else:
                    args = args[:-1]
                    kargs = (args and args[-1]) or {}
                #raw_input([arguments,kargs])

                handler = get_handler(instruction)
                handler(*args, **kargs)

        # is this working?
        for name, kls, kls_kargs in self.agents._pending:
            kls_kargs.update( { 'universe' : self } )

        # TODO: invoke managers with __call__ ?
        self.services.load()
        self.agents.load()

        # Main loop
        reactor.run()

    def sleep(self):
        """ """
        self.stop()
        for pid in self.pids['children']:
            os.system('kill -KILL '+str(pid))
        #proc.terminate()

        # hack for terminal to exit cleanly
        try: sys.exit()
        except SystemExit:
            pass

    def stop(self):
        """ """
        for service in self.services:
            try: self.services[service].obj.stop()
            except Exception,e:
                err_msg = 'Squashed exception stopping service "{service}".  Original Exception follows'.format(service=service)
                report(err_msg)
                report(str(e))
                #IP.quitting=True
        self.started = False
        for thr in self.threads:
            thr._Thread__stop()
        for p in self.procs:
            report('terminating ',p)
            p.terminate()
            p.wait()
        self.reactor.stop()

    def decide_name(self):
        """ """
        name_args = dict( alfa    = str(id(self)),
                          bravo   = getattr(self,'bravo', ''),
                          charlie = getattr(self,'charlie',''),
                          delta   = self.hostname,)
        name = 'Universe({alfa})[{bravo}:{charlie}]@{delta}'.format(**name_args)
        self.name    = name
        return name


# A cheap singleton
Universe = __Universe__()

# Set all the back-refs
Universe.agents.universe   = Universe
Universe.peers.universe    = Universe
Universe.services.universe = Universe
