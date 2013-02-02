""" cortex.services.web
"""
import os
import copy
import urllib
import webbrowser

from nevow import appserver
from twisted.web import static, server
from twisted.web.static import File
from twisted.web.client import getPage

import cortex
from cortex.core.util import report
from cortex.services import FecundService

from cortex.core.agent import Agent
from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint
from cortex.mixins.flavors import ThreadedIterator
from cortex.services.web.resource import ObjResource, EFrame
from cortex.services.web.resource.conf import ConfResource
from cortex.services.web.resource.root import Root
from cortex.services.web.resource.tree import TreeResource
from cortex.services.web.resource.plotter import Plotter, Multiplotter
from cortex.services.web.resource.redirect import Redirect
from cortex.services.web.resource.data_source import DataSource

from cortex.services.web.util import draw_ugraph

from .eventhub import EventHub
from .pchoose import PortChooser

class WebRoot(Agent, PortChooser):
    """  abstraction for / """

    def open_page_in_browser(self, url):
        report('opening: ',url)
        webbrowser.open_new_tab(url)

    def open_wui(self):
        return self.open_page_in_browser(self.url)

    def iterate(self):
        """ WebRoot is a trivial Agent with no  true concurrency
            flavor.  nothing to do here, but this iterate method will
            run exactly once.  don't use it for setup.  use setup()
            for setup.
        """

    def stop(self):
        """ TODO: stop doesn't stop anything except the
            eventhub it to turn off the webs also

            http://mumak.net/stuff/twisted-disconnect.html
        """
        self.listener.stopListening()
        super(WebRoot, self).stop()

    @property
    def static_dir(self):
        return os.path.join(
            os.path.dirname(__file__),
            'static')

    def make_data_stream(self, endpoint, fxn):
        """ attaches a datastream at the url `endpoint`.

            the datastream itself will be generated by
            consecutive calls to `fxn`, and `fxn` should
            only return values that can be used as JSON.

            `endpoint` need not start with '/'
        """
        stream = DataSource(fxn)
        self.putChild(endpoint, stream)
        return stream

    @property
    def url(self):
        return 'http://{0}:{1}'.format(self.universe.host,
                                       self.universe.port_for(self))


    def make_redirect(self, _from, b):
        """ """
        rsrc = Redirect(b)
        self.putChild(_from, rsrc)
        url = '{0}/{1}'.format(self.url, _from)
        return rsrc, url

    def setup(self):
        """ setup for several things that can be
            easily handled outside of the main loop.
        """
        favicon = os.path.join(self.static_dir, 'favicon.ico')
        self.root = Root(favicon=favicon, static=self.static_dir)
        self.putChild = self.root.putChild
        self.parent.putChild = self.putChild
        self.populate_chldren()
        site = server.Site(self.root)
        self.listener = self.universe.listenTCP(self.port, site)

    def populate_chldren(self):
        """ NB: no relationship to Agent.children() """
        self.root.parent = self # what for?
        # url that generates plots.
        # e.g. to see a plot for the datastream @ "/datastream"
        # load "/plot?endpoint=/datastream&title=some_title"
        self.putChild('plot', Plotter())
        self.putChild('_multiplot', Multiplotter(wrapped=False))
        self.putChild('multiplot', Multiplotter(wrapped=True))

        # serialized version of the universe topology.
        # this is used to generate the graph @ '/'
        self.putChild('tree.json', TreeResource(self.universe))

        # shows the current cortex configuration file
        self.putChild('conf', ConfResource(self.universe))

        # conveniences; this makes tabs for some special objects
        # really just an example of how to use ObjResource
        self.putChild('web', ObjResource(self))
        self.putChild('universe', ObjResource(self.universe))

        # the event frame
        eframe = EFrame()
        self.putChild('eframe', eframe)
        eframe.universe=self.universe#.host,self.ehub.port,chan),)
        eframe.ehub = self.parent.filter_by_type(EventHub)[0]
        # self-host the source code that's running everything.
        # really just an example of how to use static.File.
        src_dir = os.path.dirname(cortex.__file__)
        self.putChild("_code", static.File(src_dir))


class Web(FecundService):
    """ Web Service:
          start: start main webserver, and secondary event-hub
          stop:  brief description of shutdown here
    """
    class Meta:
        abstract = False
        children = [EventHub, WebRoot]

    def new_multiplot(self):
        """ """
        from cortex.services.web.util import Multiplot
        return Multiplot(self)

    def __getattr__(self,name):
        """ proxy everything I can't answer to WebRoot child """
        if not self.started:
            raise AttributeError('wont proxy getattr for "{0}" '
                                 'until after universe is started')
        else:
            return getattr(self.filter_by_type(WebRoot)[0], name)

    @constraint(boot_first='postoffice terminal'.split())
    def start(self):
        super(Web, self).start()
        terminal = (self.universe|'terminal')
        # keeping *args just so terminal can use
        # comma-style calling:  ", open_wui"
        namespace = dict(open_wui = lambda *args: self.open_wui())
        terminal.contribute_to_api(**namespace)
        report('type open_wui() to see the web user interface.')
