""" cortex.services.web.eventhub
"""
import urllib

from nevow import appserver
from twisted.web.client import getPage

from cortex.core.util import report
from cortex.mixins.flavors import ThreadedIterator
from cortex.agents.eventhandler import AbstractEventHandler
from cortex.services.web.eventhub import rootpage

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
