""" cortex.services.web
"""
import os
import time
import urllib,urllib2

from nevow import appserver
from twisted.web import static, server
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import cortex
from cortex.core.util import report
from cortex.services import Service
from cortex.core.data import EVENT_T
from cortex.util.decorators import constraint
from cortex.services.web.resource import Root, ObjResource

from cortex.services.web.eventdemo import rootpage
from cortex.mixins import LocalQueue
from cortex.mixins.flavors import ThreadedIterator
from cortex.mixins.autonomy import Autonomy

class Web(LocalQueue, Service):
    """ Web Service:
        start: start main webserver, and secondary event-hub
        stop:  brief description of shutdown here
    """
    _iteration_period = 1

    def stop(self):
        """ """
        Service.stop(self)
        report('Custom stop for', self)

    @constraint(boot_first='postoffice')
    def start(self):
        self.start_main()
        self.start_event_hub()
        (self.universe|'postoffice').subscribe(EVENT_T, self.push_q)
        Service.start(self)
        #ThreadedIterator.start(self)

    def start_main(self):
        """ """
        d          = os.path.dirname(__file__)
        code_dir   = os.path.dirname(cortex.__file__)
        static_dir = os.path.join(d, 'static')
        favicon    = os.path.join(static_dir, 'favicon.ico')

        root = Root()
        root.putChild('static',      static.File(static_dir))
        root.putChild('favicon.ico', static.File(favicon))
        root.putChild('web',         ObjResource(self))
        root.putChild('universe',    ObjResource(self.universe))
        root.putChild("_code",       static.File(code_dir))

        site = server.Site(root)
        self.universe.reactor.listenTCP(1338, site)

    def start_event_hub(self):
        """ TODO: needing an extra port for this is not cool..
        """
        tmp = rootpage.RootPage2()
        event_hub = appserver.NevowSite(tmp)
        self.universe.reactor.listenTCP(1339, event_hub)

    def _post_init(self, **kargs):
        """ initialize the local queue """
        self.init_q()

    def iterate(self):
        """ """
        report('iterating')
        return
        e = self.pop_q()
        if not e:
            return
        args, kargs = e
        report('iterating',e)
        import urllib,os
        cmd = """wget --post-data "{0}" http://127.0.0.1:1339/event/foo/blue -o -"""
        cmd = cmd.format(urllib.urlencode(dict(data=self.pop_q())))
        os.system('cd /tmp; '+cmd)
Web = ThreadedIterator.from_class(Web)

#if __name__=='__main__':
#    print ThreadedIterator.from_class(Web)
