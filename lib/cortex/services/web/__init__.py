""" cortex.services.web
"""
import os

from twisted.web import static, server

import cortex
from cortex.core.util import report
from cortex.services import Service
#from cortex.util.decorators import constraint
from cortex.services.web.resource import Root, ObjResource
from cortex.services.web.resource import ClockPage

class Web(Service):
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

    def start(self):
        """ <start> is an operation, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """
        d = os.path.dirname(__file__)
        code_dir = os.path.dirname(cortex.__file__)
        static_dir = os.path.join(d, 'static')
        favicon = os.path.join(static_dir, 'favicon.ico')

        root = Root()
        root.putChild('static',      static.File(static_dir))
        root.putChild('favicon.ico', static.File(favicon))
        root.putChild('web',         ObjResource(self))
        root.putChild("_code",       static.File(code_dir))

        site = server.Site(root)
        self.universe.reactor.listenTCP(1338, site)

        from nevow import appserver
        from twisted.application import service, internet
        from twisted.internet import reactor

        from .eventdemo import rootpage
        foo = rootpage.RootPage()

        foo.putChild('bonk',  rootpage.RootPage2())
        root.putChild('bonk', rootpage.RootPage2())

        event_hub = appserver.NevowSite(foo)
        self.universe.reactor.listenTCP(1339, event_hub)

        Service.start(self)
        report('Finished bootstrapping', self)

    def iterate(self):
        """ a placeholder for some "probably-atomic-action".
            this name is used by convention ie if <start> invokes
            it repeatedly as in from a while-loop or "reactor-recursion"
            with reactor.callLater
        """
        pass

    def play(self):
        """ <play> is stubbed out although services should usually
            override <start> instead.
        """
        return Service.play(self)
