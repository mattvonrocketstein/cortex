""" cortex.services.web
"""
import os
import urllib
import tempfile

from nevow import appserver
from twisted.web import static, server
from twisted.web.static import File
from twisted.web.client import getPage

import cortex
from cortex.core.util import report
from cortex.services import Service
from cortex.core.agent import Agent
from cortex.core.data import EVENT_T
from cortex.util.decorators import constraint
from cortex.services.web.resource import Root, ObjResource
from cortex.services.web.eventdemo import rootpage
from cortex.mixins import LocalQueue
from cortex.mixins.flavors import ThreadedIterator
from cortex.core.agent.manager import AgentManager


def doit(k, fname, report):
    """ actually build a graph"""
    import networkx as nx
    from pygraphviz import *
    G = nx.Graph()
    G.add_edges_from(k)
    A=nx.to_agraph(G)
    H = nx.from_agraph(A)
    A.edge_attr['color']='red'
    A.layout()
    A.draw(fname)
    #A.graph_attr['label']='known universe topology'
    #nx.draw(A)
    #nx.draw_random(G)
    #nx.draw_spectral(G)
    #nx.draw_graphviz(G) #nx.write_dot(G,'file.dot')
    #nx.draw_random(G) #nx.draw_circular(G)

class EventHandlerAgent(LocalQueue, Agent):

    class Meta:
        subscriptions = {EVENT_T: 'push_q'}

    def start(self):
        self.init_q() # safe to call in start or __init__
        super(EventHandlerAgent, self).start()

    def iterate(self):
        """ """
        e = self.pop_q()
        if e:
            self.handle_event(e)

    def handle_event(self, e):
        raise TypeError('not implemented error')

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

def ugraph(universe):
    """ builds an adjacency matrix for the universe topology:
        a list of tuples where every tuple is parent -> child

        TODO: a real traversal for arbitrary depth
    """
    stuff = universe.children() + [universe]
    stuff = [[x, x.children()] for x in stuff if hasattr(x, 'children')]
    stuff = dict(stuff)
    name = lambda q: q.name if q!=universe else 'universe'
    out = []
    for node, children in stuff.items():
        for z in children:
            out.append( (name(node), name(z)) )
    return out


class WebRoot(Agent):
    """ TODO: smarter if you can't import networkx et al '"""

    def iterate(self):
        self.graph_f = tempfile.mktemp() + '.png'
        self.root.putChild('ugraph.png', File(self.graph_f))
        self.universe.callInProcess(doit,
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
class EventHub(EventHandlerAgent):

    POST_HDR    = {'Content-Type':
                   "application/x-www-form-urlencoded;charset=utf-8"}

    @property
    def port(self):
        return 1339

    def handle_event(self, e):
        """ """
        args, kargs = e
        peer        = args[0]
        url      = 'http://127.0.0.1:1339/event/'
        values   = getattr(peer, '__dict__', dict(data=peer))
        postdata = urllib.urlencode(values)
        def callback(*args): "any processing on page string here."
        def errback(*args): report('error with getPage:',str(args))
        getPage(url, headers=EventHub.POST_HDR, method="POST",
                postdata=postdata).addCallback(callback, errback)

    def start(self):
        super(EventHub, self).start()
        tmp = rootpage.RootPage2()
        event_hub = appserver.NevowSite(tmp)
        self.universe.reactor.listenTCP(self.port, event_hub)
