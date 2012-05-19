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
from cortex.services.web.eventdemo import rootpage
from cortex.mixins.flavors import ThreadedIterator
from cortex.core.agent.manager import AgentManager
from cortex.services.web.resource import Root, ObjResource
from cortex.agents.eventhandler import AbstractEventHandler
from cortex.services.web.util import draw_ugraph, ugraph


class Web(LocalQueue, Service, AgentManager):
    """ Web Service:
        start: start main webserver, and secondary event-hub
        stop:  brief description of shutdown here
    """

    # NOTE: currently this is the time it will take for shutdown too :(
    _iteration_period = 2

    __str__  = Service.__str__
    __repr__ = Service.__repr__

    def __init__(self, *args, **kargs):
        Service.__init__(self, **kargs)
        AgentManager.__init__(self, **kargs)

    def stop(self):
        """ TODO: put am.stop_all() in service? """
        Service.stop(self)
        AgentManager.stop_all(self)

    @constraint(boot_first='postoffice')
    def start(self):
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
            make for to turn off the webs also """
        super(WebRoot, self).stop()
        if hasattr(self,'graph_f'):
            report('wiping graph file')
            os.remove(self.graph_f)

    def setup(self):
        d          = os.path.dirname(__file__)
        static_dir = os.path.join(d, 'static')
        favicon    = os.path.join(static_dir, 'favicon.ico')
        self.root  = Root(favicon=favicon, static=static_dir)
        self.root.putChild('web',         ObjResource(self))
        self.root.putChild('universe',    ObjResource(self.universe))
        self.root.putChild("_code",       static.File(os.path.dirname(cortex.__file__)))
        site       = server.Site(self.root)
        self.universe.reactor.listenTCP(1338, site)

@ThreadedIterator.from_class
class EventHub(AbstractEventHandler):

    POST_HDR    = {'Content-Type':
                   "application/x-www-form-urlencoded;charset=utf-8"}

    @property
    def port(self):
        return 1339

    def handle_event(self, e):
        """ """
        args, kargs = e
        peer        = args[0]
        url         = 'http://127.0.0.1:1339/event/'
        values      = getattr(peer, '__dict__', dict(data=peer))
        postdata    = urllib.urlencode(values)
        def callback(*args): "any processing on page string here."
        def errback(*args): report('error with getPage:',str(args))
        getPage(url, headers=EventHub.POST_HDR, method="POST",
                postdata=postdata).addCallback(callback, errback)

    def setup(self):
        tmp = rootpage.RootPage2()
        event_hub = appserver.NevowSite(tmp)
        self.universe.reactor.listenTCP(self.port, event_hub)
