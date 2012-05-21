""" cortex.services.web
"""
import os
import copy
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

class FecundService(Service, AgentManager):
    """ FecundService describes a service with children.

        You get mostly the semantics you'd expect.  When the
        parent is start()'ed, the children start, and similarly
        for stop().

        To use, subclassers should define a Meta like this:


           class Meta:
               children = [ChildClass-1, ChildClass-2, .. ]
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kargs):
        Service.__init__(self, **kargs)
        AgentManager.__init__(self, **kargs)

    def start(self):
        """ """
        ctx = dict(universe=self.universe)
        child_classes = self.__class__.Meta.children
        for kls in child_classes:
            name = kls.__name__
            kargs = dict(kls=kls, kls_kargs=ctx, name=name)
            self.manage(**kargs)
        self.load()
        Service.start(self)


class WebRoot(Agent):
    """ TODO: act smarter if you can't import networkx et al '"""

    def iterate(self):
        """ WebRoot is a trivial Agent with no  true concurrency
            flavor.  this iterate method will run once, and runs
            only after the system is otherwise bootstrapped.  we
            call the draw_ugraph using multiprocessing, because
            something about the implementation of matplotlib/nx
            or whatever else wants the main thread.  doing this
            instead with callInThread, callFromThread, etc, have
            all been tried, and although they might even seem to
            work initially it seems to also leak memory or
            something
        """
        self.graph_f = self.universe.tmpfname(suffix='png')
        self.root.putChild('ugraph.png', File(self.graph_f))
        self.universe.callInProcess(draw_ugraph,
                                    name='drawing to file@' + self.graph_f,
                                    args = ( ugraph(self.universe),
                                             self.graph_f, report ) )

    def stop(self):
        """ TODO: stop doesn't stop anything except the
                   eventhub it to turn off the webs also

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
        """ setup for several things that can be
            easily handled outside of the main loop.
        """
        d          = os.path.dirname(__file__)
        static_dir = os.path.join(d, 'static')
        favicon    = os.path.join(static_dir, 'favicon.ico')
        self.root  = Root(favicon=favicon, static=static_dir)
        self.root.putChild('web',         ObjResource(self))
        self.root.putChild('universe',    ObjResource(self.universe))
        self.root.putChild("_code",       static.File(os.path.dirname(cortex.__file__)))
        site       = server.Site(self.root)
        self.listener = self.universe.listenTCP(1338, site)

class Web(FecundService):
    """ Web Service:
        start: start main webserver, and secondary event-hub
        stop:  brief description of shutdown here
    """
    class Meta:
        children = [EventHub, WebRoot]

    @constraint(boot_first='postoffice')
    def start(self): super(Web, self).start()
