""" cortex.core.universe
"""

import inspect
import simplejson
from twisted.internet import reactor

from cortex.core.util import report, console
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin

class __Universe__(object, AutonomyMixin, PerspectiveMixin):
    """
        NOTE: this should effectively be a singleton
    """

    node_list = []

    class shell:
        def __init__(self, path):
            self.path = path

        def __call__(self, line, quiet=False):
            """ """
            os.system('cd "'+path+'"; '+line)

    @property
    def nodeconf(self):
        """ iterator that returns decoded json entries from self.nodeconf_file
        """
        report("Universe.nodeconf: decoding")
        x = open(self.nodeconf_file).readlines()
        x = [z.strip() for z in x]
        nodes = []
        for line in x:
            if not line:
                continue
            report('got line',line)
            try:
                nodedef = simplejson.loads(line)
            except:
                report("error decoding..", line)
            else:
                report('encoded..', nodedef) #console.color(str(nodedef))
                nodes.append(nodedef)
        return nodes

    def play(self):
        """
            Post:
                  self.node_list = [ <list of active nodes> ]
        """
        report("Universe.play!")

        # Starts all nodes registered via the nodeconf
        for node in self.nodeconf:
            name,kargs = node
            kargs.update( {'name':name} )
            node = self.launch_instance(**kargs)
            self.node_list.append(node)

        # Start special services provided by the universe
        self.stdoutbeacon_service()
        self.terminal_service()
        #self.filercvr()

        # Main loop
        reactor.run()

    def django_service(self):
        """  Start special services provided by the universe """
        import django.core.handlers.wsgi
        application = django.core.handlers.wsgi.WSGIHandler()

    def stdoutbeacon_service(self,beacon=None):
        """  Start special services provided by the universe """
        if not beacon:
            def beacon():
                reactor.callLater(1,beacon)
                print " blip "
        reactor.callLater(1,beacon)

    def terminal_service(self):
        """  Start special services provided by the universe

               Adapted from:
                 http://code.activestate.com/recipes/410670-integrating-twisted-reactor-with-ipython/


        # Sample usage.

        # Create the shell object. This steals twisted.internet.reactor
        # for its own purposes, to make sure you've already installed a
        # reactor of your choice.

        # Run the mainloop.  This runs the actual reactor.run() method.
        # The twisted.internet.reactor object at this point is a dummy
        # object that passes through to the actual reactor, but prevents
        # run() from being called on it again.

        # You must exit IPython to terminate your program.
        """
        from cortex.core import api
        from cortex.core.terminal import IPShellTwisted, IPY_ARGS
        universe = {'__name__': '__cortex_shell__'}
        universe.update(api.publish())
        shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe)
        shell.mainloop()
        report('the Terminal Service Dies.')

    def launch_instance(self, **kargs):
        from cortex.core.node import Node
        report(**kargs)
        node = Node(**kargs)
        report(node)
        console.draw_line()
        node.play()
        return node

Universe = __Universe__()
