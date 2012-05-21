""" cortex.services.web
"""
import os
import urllib

from nevow import appserver
from twisted.web import static, server
from twisted.web.static import File
from twisted.web.client import getPage

import cortex
from cortex.core.util import report
from cortex.services import Service
from cortex.core.agent import Agent
from cortex.core.data import EVENT_T
from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint
from cortex.mixins.flavors import ThreadedIterator
from cortex.core.agent.manager import AgentManager
from cortex.services.web.resource import Root, ObjResource
from cortex.services.web.util import draw_ugraph, ugraph

from .eventhub import EventHub

class Web(Service, AgentManager):
    """ Web Service:
        start: start main webserver, and secondary event-hub
        stop:  brief description of shutdown here
    """

    def __init__(self, *args, **kargs):
        Service.__init__(self, **kargs)
        AgentManager.__init__(self, **kargs)

    @constraint(boot_first='postoffice')
    def start(self):
        """ TODO: move these children to Meta.children=[] .. """
        ctx = dict(universe=self.universe)
        for kls in [EventHub, WebRoot]:
            self.manage(kls=kls, kls_kargs=ctx,
                        name=kls.__name__)
        self.load()
        Service.start(self)

class WebRoot(Agent):
    """ TODO: smarter if you can't import networkx et al '"""

    def iterate(self):
        self.graph_f = self.universe.tmpfname(suffix='png')
        self.root.putChild('ugraph.png', File(self.graph_f))
        self.universe.callInProcess(draw_ugraph,
                                    name='drawing to file@' + self.graph_f,
                                    args = ( ugraph(self.universe),
                                             self.graph_f, report ) )

    def stop(self):
        """ TODO: stop doesn't stop anything except the eventhub..
            make for to turn off the webs also

            http://mumak.net/stuff/twisted-disconnect.html
        """
        self.listener.stopListening()
        super(WebRoot, self).stop()
        if hasattr(self,'graph_f'):
            report('wiping graph file')
            try: os.remove(self.graph_f)
            except OSError,e:
                report("Ignoring error: "+str(e))

    def setup(self):
        d          = os.path.dirname(__file__)
        static_dir = os.path.join(d, 'static')
        favicon    = os.path.join(static_dir, 'favicon.ico')
        self.root  = Root(favicon=favicon, static=static_dir)
        self.root.putChild('web',         ObjResource(self))
        self.root.putChild('universe',    ObjResource(self.universe))
        self.root.putChild("_code",       static.File(os.path.dirname(cortex.__file__)))
        site       = server.Site(self.root)
        self.listener = self.universe.listenTCP(1338, site)
