""" cortex.core.universe

      The universe is an abstraction intended to unify the representation
      of aspects of the interpretter, the operating system, the "mainloop",
      and the cortex runtime.  It should (probably) effectively be a singleton--
      one per process.
"""

import os, sys
import multiprocessing
import inspect, types
from tempfile import NamedTemporaryFile

import simplejson
from twisted.internet import reactor

from cortex.util import Memoize
from cortex.core.util import get_mod
from cortex.core.reloading import AutoReloader
from cortex.core.parsing import Nodeconf
from cortex.core.util import report, console
from cortex.core.data import SERVICES_DOTPATH
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.atoms import PersistenceMixin
from cortex.core.peer import PeerManager, PEERS
from cortex.core.service import Service, SERVICES
from cortex.core.service import ServiceManager
from cortex.core.node import AGENTS #AgentManager
from cortex.mixins import OSMixin, PIDMixin
from cortex.core.notation import UniverseNotation

class __Universe__(AutoReloader, OSMixin, UniverseNotation,
                   AutonomyMixin, PerspectiveMixin, PersistenceMixin):
    """ """
    system_shell  = 'xterm -fg green -bg black -e '
    reactor       = reactor
    services      = SERVICES
    peers         = PEERS
    agents        = AGENTS
    #clones        = CloneManager()
    #processes     = ProcessManager()
    nodeconf_file = u''

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
        #raise Exception,jsons
        return jsons

    @property
    def Nodes(self):
        """ nodes: static definition """
        blammo = getattr(self, '_use_nodeconf', self.read_nodeconf)
        #, self.read_nodeconf()
        return blammo()

    @property
    def nodes(self):
        """ nodes: dynamic definition """


    def play(self):
        """
            Post-conditions:
        """
        report("Universe.play!")
        self.decide_name()
        self.started = True
        from cortex.core import api as API
        from cortex.core.api import publish
        _api = publish()
        def parse_error(error, instruction, args, kargs, api=_api):
            import platform, inspect, pprint, StringIO
            api_header = "Cortex-API @ {H}://{F}"
            api_header = api_header.format(F=API,
                                           H=platform.node(),)
            fhandle    = StringIO.StringIO(); pprint.pprint(api, fhandle)
            api_body   = ''# fhandle.getvalue()
            zapi   = api_header + api_body
            #api_body   = '\n'.join(([x[0] for x in api.items()]))
            opts   = dict(api=zapi, instruction=instruction,args=args,kargs=kargs)
            header = "ParseError: {E}:".format(E=error)
            body   = """
            instruction = {instruction}
            args        = {args}
            kargs       = {kargs}
            with api    = {api}
            """
            error  = (header + body).format(**opts)
            print error
            sys.exit()

        def get_handler(instruction):
            """ grab an item named "instruction" from the api """
            return _api.get(instruction)

        # Interprets all the instructions in the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.Nodes:
            #for node in self.read_nodeconf():
                original = node
                instruction, args = node[0], node[1:]

                report("parsing node", node)
                if len(args)==1:
                    kargs = {}
                else:
                    args = args[:-1]
                    kargs = (args and args[-1]) or {}
                #raw_input([arguments,kargs])

                handler = get_handler(instruction)
                if not handler:
                    parse_error("No instruction handler!", instruction, args, kargs)
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

    def fault(self, error, context):
        """ TODO: sane yet relatively automatic logging for faults.
        """
        console.vertical_space()
        report("",header=console.red("--> FAULT <--"))
        console.draw_line()
        print ( "\n{error}".format(error=error))
        import StringIO, pprint
        fhandle=StringIO.StringIO()
        pprint.pprint(context, fhandle)
        print console.color(fhandle.getvalue())
        console.draw_line()
        console.vertical_space()
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()

    def loadService(self, service, **kargs):
        """ """
        if isinstance(service, types.StringTypes):
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
                mod_name = service
                try: mod = get_mod(mod_name)
                except (AttributeError,ImportError), e:
                    self.fault("Failed to get module '{mod}' to load service.".format(mod=mod_name),
                               dict(exception=e))
                    mod = {}
                else:
                    if mod==AttributeError: mod = {}
                ret_vals = []
                for name, val in mod.items():
                    if inspect.isclass(val):
                        if not val==Service and issubclass(val, Service):
                            #report('discovered service in ' + mod_name)
                            if not getattr(val, 'do_not_discover', False):
                                ret_vals.append(self.start_service(val, ask=False, **kargs)) # THUNK
                return ret_vals

        # Not a string? let's hope it's already a service-like thing
        else:
            return self.start_service(service, **kargs)


    def start_service(self, obj, ask=False, **kargs):
        """ obj is actually a service_kls?
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
