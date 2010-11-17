""" cortex.core.universe
"""

import os, sys
import inspect
import simplejson
import multiprocessing
from tempfile import NamedTemporaryFile

from twisted.internet import reactor

from cortex.util import Memoize
from cortex.core.reloading import AutoReloader
from cortex.core.util import report, console
from cortex.core.data import SERVICES_DOTPATH
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.atoms import PersistenceMixin
from cortex.core.peer import PeerManager, PEERS
from cortex.core.service import Service
from cortex.core.service import ServiceManager

from cortex.core.mixins import OSMixin, PIDMixin
from cortex.core.mixins import EventMixin, NoticeMixin

class __Universe__(AutoReloader, PIDMixin,
                   NoticeMixin, AutonomyMixin,
                   PerspectiveMixin, PersistenceMixin):
    """
        NOTE: this should effectively be a singleton
    """
    node_list = []
    _services = []
    reactor   = reactor
    peers     = PEERS

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

    def tmpfile(self):
        """ return a new temporary file """
        tmpdir = os.path.join(self.instance_dir, 'tmp')
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        f = NamedTemporaryFile(delete=False,dir=tmpdir)
        return f

    def leave(self, other=None):
        """ other begs universe for permission to leave """
        #self.nodes.remove()
        def detect_other():
            pass
        if other==None:
            other = detect_other()
        pass

    def read_nodeconf(self):
        """ iterator that returns decoded json entries from self.nodeconf_file
        """
        assert hasattr(self, 'nodeconf_file') and self.nodeconf_file, 'Universe.nodeconf_file tests false or is not set.'
        #report("Universe.nodeconf: decoding")
        x = open(self.nodeconf_file).readlines()
        x = [z.strip() for z in x]
        nodes = []
        for line in x:
            # Respect comments and disregard empties
            if not line or line.startswith('#'):

                continue
            #report('got line', line)
            try:
                nodedef = simplejson.loads(line)
            except:
                report("error decoding..", line)
            else:
                #report('encoded..', nodedef)
                nodes.append(nodedef)
        return nodes

    @property
    def Nodes(self):
        """ nodes: static definition """
        return self.read_nodeconf()

    @property
    def nodes(self):
        """ nodes: dynamic definition """
        return self.node_list

    def stop(self):
        """ """
        for service in self.services:
            try: service.stop()
            except Exception,e:
                print 'exc',e
                #IP.quitting=True
        self.started = False
        for thr in self.threads:
            thr._Thread__stop()
        self.reactor.stop()

    def play(self):
        """
            Post-conditions:
                self.node_list = [ <list of active nodes> ]
        """
        report("Universe.play!")
        self.name    = 'Universe-' + str(id(self)) + '@' + self.hostname
        self.started = True
        def get_handler(instruction):
            from cortex.core.api import publish
            _api = publish()
            return _api.get(instruction)

        # Interprets all the instructions in the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.read_nodeconf():
                original = node
                #node.reverse()
                #instruction = node.pop()
                instruction,node=node[0],node[1:]
                if len(node)==1:
                    arguments = node
                    kargs={}
                else:
                    arguments = node[:-1]
                    kargs = node[-1]
                #raw_input([arguments,kargs])
                handler = get_handler(instruction)
                handler(*arguments, **kargs)

        # Start special services provided by the universe
        for service in self.Services:
            report('launching service', service)
            self.loadService(service)

        # Main loop
        reactor.run()

    def loadService(self, service, **kargs):
        """ """
        if isinstance(service, str):
            # handle dotpaths
            if "." in service:
                service = service.split('.')
                if len(service) == 2:
                    mod_name, class_name = service
                    namespace = get_mod(mod_name)
                    if class_name in namespace:
                        service_obj = namespace[class_name]
                        return self.start_service(service_obj, **kargs)
                else:
                    raise Exception,'will not interpret that dotpath yet'

            # just one word.. where/what could it be?
            else:
                mod_name = service
                ret_vals = []
                for name, val in get_mod(mod_name).items():
                    if inspect.isclass(val):
                        if not val==Service and issubclass(val, Service):
                            #launch_service = lambda: val(universe=self).play
                            report('discovered service in ' + mod_name)
                            ret_vals.append(self.start_service(val,ask=False,**kargs))
                return ret_vals

        # Not a string? let's hope it's already a service-like thing
        else:
            return self.start_service(service, **kargs)


    def start_service(self, service_obj, ask=False, **kargs):
        """ """
        if ask:
            raise Exception,'niy'
            getAnswer('launch service@'+str([name, val]),
                      yesAction=service_obj(universe=self, **kargs).play)
            return service_obj # TODO: return service_obj.play()
        else:
            ret = service_obj(universe=self, **kargs).play()
            self._services.append(ret)
            return ret

    @property
    #@Memoize
    def services(self):
        """ services: dynamic definition

            this represents services that have already been
            successfully started.
        """
        out = ServiceManager()
        for s in self._services:
            out.register(s.__class__.__name__.lower(),
                         service_obj=s)
            #dict([[s.__class__.__name__.lower(),s] for s in self._services])
        return out

    @property
    def Services(self):
        """ services: static definition

            computes services from defaults,
             command line arguments, and
              node definition files.

            TODO: move this stuff into nodeconf
        """

        from cortex.services.terminal import Terminal
        from cortex.services.beacon import Beacon
        from cortex.services._linda import Linda
        _Services = [Linda, Terminal]
        # _Services.append(Beacon); _Services.append(self.stdoutbeacon_service)
        #_Services.append(self.filercvr)
        return _Services

    def launch_instance(self, **kargs):
        """ """
        from cortex.core.node import Node
        report(**kargs)
        node = Node(**kargs)
        report(node)
        console.draw_line()
        node.play()
        return node

Universe = __Universe__()
def get_mod(mod_name, root_dotpath=SERVICES_DOTPATH):
    """ stupid helper to snag modules from inside the services root """
    out = {}
    ns  = {}
    exec('from ' + root_dotpath + ' import ' + mod_name + ' as mod', ns)
    mod = ns['mod']

    for name in dir(mod):
        val = getattr(mod, name)
        out[name] = val
    return out
