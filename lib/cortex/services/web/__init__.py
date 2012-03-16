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
from cortex.services.web.resource import ClockPage
from cortex.services.web.resource import Root, ObjResource

from .eventdemo import rootpage
from cortex.mixins import LocalQueue

class Web(Service, LocalQueue):
    """ Stub Service:
        start: brief description of service start-up here
        stop:  brief description service shutdown here
    """
    def print_error(self, *errors):
        """ """
        for x in errors:
            pass # choose any errors to ignore and remove them
        report('error_handler for generic service', str(errors) )

    def stop(self):
        """ """
        Service.stop(self)
        report('Custom stop for', self)

    @constraint(boot_first='postoffice')
    def start(self):
        """ <start> is an operation, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """
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
        event_hub = appserver.NevowSite(rootpage.RootPage2())
        self.universe.reactor.listenTCP(1338, site)
        self.universe.reactor.listenTCP(1339, event_hub)
        self.universe.reactor.callFromThread(self.iterate)
        (self.universe|'postoffice').subscribe(EVENT_T, self.push_q)
        go = lambda: self.universe.threadpool.callInThread(self.run)
        self.universe.reactor.callWhenRunning(go)
        Service.start(self)

    def run(self):
        """ see docs for ThreadedIterator """
        while self.started:
            self.iterate()


    def _post_init(self, syndicate_events_to_terminal=True):
        """ install back-reference in universe,
            initialize the local queue
        """
        # initialize for LocalQueue
        self.init_q()

    def update_events(self, *args, **kargs):
        url = 'http://127.0.0.1:1339/event/foo/blue'
        data = urllib.urlencode(dict(args=args,kargs=kargs))
        req = urllib2.Request(url)
        fd = urllib2.urlopen(req, data)
        print fd.read()
        #cmd = """wget --post-data "{0}" http://127.0.0.1:1339/event/foo/blue -o -"""
        #cmd = cmd.format(urllib.urlencode(dict(args=args,kargs=kargs)))
        #os.system('cd /tmp; '+cmd)

    def iterate(self):
        """ a placeholder for some "probably-atomic-action".
            this name is used by convention ie if <start> invokes
            it repeatedly as in from a while-loop or "reactor-recursion"
            with reactor.callLater
        """
        e = self.pop_q()
        if not e:
            time.sleep(1)
            return
        args, kargs = e
        report('iterating',e)
        time.sleep(1)
        import urllib,os
        cmd = """wget --post-data "{0}" http://127.0.0.1:1339/event/foo/blue -o -"""
        cmd = cmd.format(urllib.urlencode(dict(data=self.pop_q())))
        os.system('cd /tmp; '+cmd)

    def play(self):
        """ <play> is stubbed out although services should usually
            override <start> instead.
        """
        return Service.play(self)
