""" cortex.services.web
    TODO: constraint solving is sometimes broken?
        determined boot order:', ['web', 'postoffice', 'terminal', 'linda', 'mapper', 'api']
    TODO: occasional message delivery issues or unintended queue sharing?

"""
import os
import time
import urllib

from nevow import appserver
from twisted.web import static, server
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.web.client import HTTPClientFactory, getPage
from twisted.internet.task import LoopingCall
import cortex
from cortex.core.util import report
from cortex.services import Service
from cortex.core.agent import Agent
from cortex.core.data import EVENT_T
from cortex.util.decorators import constraint
from cortex.services.web.resource import Root, ObjResource, NavResource

from cortex.services.web.eventdemo import rootpage
from cortex.mixins import LocalQueue
from cortex.mixins.flavors import ThreadedIterator
from cortex.core.agent.manager import AgentManager
from cortex.mixins.autonomy import Autonomy

#class Web(Service, AgentManager):
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
        """ """
        Service.stop(self)
        AgentManager.stop_all(self)
        report('Custom stop for', self)

    @constraint(boot_first='postoffice')
    def start(self):
        ctx = dict(universe=self.universe)
        for kls in [EventHub, WebRoot]:
            self.manage(kls=kls, kls_kargs=ctx,
                        name=kls.__name__)
        self.load()

        Service.start(self)


class WebRoot(Agent):
    def start(self):
        d          = os.path.dirname(__file__)
        static_dir = os.path.join(d, 'static')
        favicon    = os.path.join(static_dir, 'favicon.ico')
        root = Root(favicon=favicon, static=static_dir)
        site = server.Site(root)
        root.putChild('web',         ObjResource(self))
        root.putChild('universe',    ObjResource(self.universe))
        root.putChild("_code",       static.File(os.path.dirname(cortex.__file__)))
        self.universe.reactor.listenTCP(1338, site)

class EventHub(LocalQueue, Agent):
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
        values   = peer.__dict__
        postdata = urllib.urlencode(values)

        def callback(*args): "any processing on page string here."
        def errback(*args): report('error with getPage:',str(args))
        callbacks = (callback, errback)
        getPage(url, headers=EventHub.POST_HDR,
                method="POST", postdata=postdata).addCallback(*callbacks)

    def start(self):
        self.init_q() # safe to call in start or __init__
        tmp = rootpage.RootPage2()
        event_hub = appserver.NevowSite(tmp)
        self.universe.reactor.listenTCP(self.port, event_hub)
        (self.universe|'postoffice').subscribe(EVENT_T, self.push_q)

    def iterate(self):
        """ """
        e = self.pop_q()
        if e:
            self.handle_event(e)


Web = ThreadedIterator.from_class(Web)
EventHub = ThreadedIterator.from_class(EventHub)
