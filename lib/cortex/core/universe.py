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
from cortex.core.service import AgentManager
from cortex.mixins import OSMixin, PIDMixin
from cortex.core.notation import UniverseNotation

class __Universe__(AutoReloader, OSMixin, UniverseNotation,
                   AutonomyMixin, PerspectiveMixin, PersistenceMixin):
    """ """
    system_shell  = 'xterm -fg green -bg black -e '
    reactor       = reactor
    services      = SERVICES
    peers         = PEERS
    agents        = AgentManager()
    nodeconf_file = ''

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

        def get_handler(instruction):
            """ grab an item named "instruction" from the api """
            from cortex.core.api import publish
            _api = publish()
            return _api.get(instruction)

        # Interprets all the instructions in the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.Nodes:
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


        self.services.load()
        for name, kls, kls_kargs in self.agents._pending:
            kls_kargs.update({'universe':self})
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
                        #raise e
                        report("Failed to get module {mod} to load service.".format(mod=mod_name))
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
                except ImportError, e:
                    report("Failed to get module '{mod}' to load service.".format(mod=mod_name))
                    mod = {}

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

Universe       = __Universe__()
PEERS.universe = Universe
