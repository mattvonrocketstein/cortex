""" cortex.core.universe
"""
import os
import sys
import inspect
import simplejson
from peak.util.imports import lazyModule
from tempfile import NamedTemporaryFile
from twisted.internet import reactor

from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.atoms import PersistenceMixin
from cortex.util import Memoize
from cortex.core.reloading import AutoReloader
from cortex.core.helpers import get_mod
from cortex.core.util import report, console
from cortex.core.services import ServiceManager, Service

api = lazyModule('cortex.core.api')

class EventMixin(object):
    def push_events(self, *args):
        [self.push_event(arg) for arg in args]

    def push_event(self,notice):
        self.ground.add( ('system_event', notice) )

    @property
    def events(self):
        """ """
        return self.ground.get_many( ('system_event', object) )


class __Universe__(AutoReloader, AutonomyMixin, PerspectiveMixin,
                   PersistenceMixin, EventMixin):
    """
        NOTE: this should effectively be a singleton
    """
    node_list = []
    _services = []
    reactor   = reactor

    def sleep(self):
        """ """

        self.stop()

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
            try:
                nodedef = simplejson.loads(line)
            except:
                report("error decoding..", line)
            else:
                nodes.append(nodedef)
        return nodes

    @property
    def Nodes(self):
        """ nodes: static definition """
        return self.read_nodeconf()

    @property
    def threads(self):
        import threading
        return threading.enumerate()

    @property
    def nodes(self):
        """ nodes: dynamic definition """
        return self.node_list

    def stop(self):
        """
        """
        super(__Universe__, self).stop()
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
        super(__Universe__,self).play()

        # Starts all nodes registered via the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.read_nodeconf():
                original = node
                node.reverse()
                instruction = node.pop()
                arguments   = node
                _api = api.publish()
                if instruction in _api:
                    handler = _api.get(instruction)
                    handler(*arguments)
                else:
                    raise NodeconfSyntaxError,original

        # Start special services provided by the universe
        for service in self.Services:
            report('launching service', service)
            self.loadService(service)

        # Main loop
        reactor.run()

    def loadService(self,service):
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
                        return self.start_service(service_obj)
                else:
                    raise Exception,'will not interpret that dotpath yet'

            # just one word.. what could it be?
            else:
                mod_name = service
                ret_vals = []
                for name, val in get_mod(mod_name).items():
                    if inspect.isclass(val):
                        if not val==Service and issubclass(val, Service):
                            #launch_service = lambda: val(universe=self).play
                            report('discovered service in ' + mod_name)
                            ret_vals.append(self.start_service(val,ask=False))
                return ret_vals

        # Not a string? let's hope it's already a service-like thing
        else:
            return self.start_service(service)


    def start_service(self, service_obj, ask=False):
        """ """
        if ask:
            raise Exception,'niy'
            getAnswer('launch service@'+str([name, val]),
                      yesAction=service_obj(universe=self).play)
            #return..
        else:
            ret = service_obj(universe=self).play()
            self._services.append(ret)
            return ret

    @property
    @Memoize
    def services(self):
        """ services: dynamic definition

            this represents services that have already been
            successfully started.
        """
        return ServiceManager(self._services)

    @property
    def Services(self):
        """ services: static definition

            computes services from defaults,
             command line arguments, and
              node definition files.

            TODO: move this stuff into nodeconf
        """

        from cortex.core.services.terminal import Terminal
        from cortex.core.services.beacon import Beacon
        from cortex.core.services._linda import Linda
        _Services = [Linda, Terminal]
        # _Services.append(Beacon)
        #_Services.append(self.stdoutbeacon_service)
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
Universe.name    = 'Universe' + str(id(Universe))

