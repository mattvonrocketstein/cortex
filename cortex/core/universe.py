""" cortex.core.universe
"""

import inspect
import simplejson
from twisted.internet import reactor
from cortex.util import Memoize
from cortex.core.util import report, console
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.services import ServiceManager

class __Universe__(object, AutonomyMixin, PerspectiveMixin):
    """
        NOTE: this should effectively be a singleton
    """

    node_list = []
    _services = []

    """
    class shell:
         a dumb abstraction for a shell rooted at <path>
        def __init__(self, path):
            self.path = path

        def __call__(self, line, quiet=False):
            """ """
            os.system('cd "'+path+'"; '+line)
    """
    reactor = reactor

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
            if not line:
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

    def play(self):
        """
            Post:
                self.node_list = [ <list of active nodes> ]
        """
        report("Universe.play!")

        # Starts all nodes registered via the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.read_nodeconf():
                name, kargs = node
                kargs.update( {'name':name,'universe':self} )
                node = self.launch_instance(**kargs)
                self.node_list.append(node)

        # Start special services provided by the universe
        for service in self.Services:
            self._services.append(service(universe=self).play())

        report('running reactor')

        # Main loop
        #reactor.run()

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
        """
        #[self.stdoutbeacon_service, self.filercvr]
        from cortex.core.services.terminal import Terminal
        from cortex.core.services.beacon import Beacon
        from cortex.core.services._linda import Linda
        return [Linda,Terminal ] #Beacon]

    def django_service(self):
        """  Start special services provided by the universe """
        import django.core.handlers.wsgi
        application = django.core.handlers.wsgi.WSGIHandler()

    def launch_instance(self, **kargs):
        from cortex.core.node import Node
        report(**kargs)
        node = Node(**kargs)
        report(node)
        console.draw_line()
        node.play()
        return node

Universe = __Universe__()
