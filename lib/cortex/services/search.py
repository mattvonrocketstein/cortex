""" cortex.services.search

      a search service

      TODO: have ACKer instances removed from search.agents automatically when complete
      TODO: make 'bus' less special, parametrizing it somehow
      TODO: make google search service, optionally using domain names
      TODO: make wikipedia search service
      TODO: stop using UUID, key on search term and disallow multiple running simultaneously
      TODO: result caching?
"""
from channel import Channel

from cortex.core.util import report
from cortex.services import Service
from cortex.util.pyack import pyack
from cortex.mixins.flavors import Threaded
from cortex.util.decorators import constraint
from cortex.core.agent.manager import AgentManager

MAX_RESULTS = 5

class Search(Service, AgentManager):
    """ Search Service:
          spawn robots to search google, stackoverflow, django-docs.
          robots run in the background and call back the shell when
          they're finished.
    """

    def __init__(self, *args, **kargs):
        Service.__init__(self, *args, **kargs)
        AgentManager.__init__(self, *args, **kargs)

    @constraint(boot_first='postoffice')
    def start(self):
        """ <start> is an operation, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
            """
        report('starting')
        Service.start(self)
        poffice = (self.universe|'postoffice')

        # 'bus' name is important here.  it is assumed by from_function functions.
        # if that is a requirement.. doesn't it make sense that actually parents
        # should themselves extend bus

        self.bus = Channel.search_bus
        self.bus.bind(poffice)
        self.bus.subscribe(self.search_callback)
        report('finished')

    @property
    def uuid(self):
        import uuid
        return str(uuid.uuid1())

    def spawn_searcher(self, wd, search):
        """ """
        report('spawning search for "{0}", starting from "{1}"'.format(search,wd))
        #return self(ACKer, name='Phase1:VeryLocal:'+self.uuid, wd=wd, search=search)
        return self(GGLer, name='Phase1:Internet:' + self.uuid, wd=wd, search=search)

    def search_callback(self, results, **kargs):
        msg = 'Searcher {0} finished, unpacked {1} results total.  top {2}'
        report(msg.format('(unknown)', len(results), MAX_RESULTS))
        report.pprint(results.weighted[:MAX_RESULTS])
        self.results = results

    def h(self, search_string):
        import os
        working_dir = os.getcwd()
        self.spawn_searcher(working_dir, search_string)

from xgoogle.search import GoogleSearch, SearchError
def search_with_google(search=None, **kargs):
    try:
        gs = GoogleSearch("quick and dirty")
        gs.results_per_page = 50
        results = gs.get_results()
        for res in results:
            report(res.title.encode('utf8'))
            #print res.desc.encode('utf8')
            report(res.url.encode('utf8'))
    except SearchError, e:
        report("Search failed: %s" % e)
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
GGLer = Threaded.from_function(search_with_google)

def search_with_ack(wd=None, search=None):
    """ """
    acker = pyack('{search} {dir}'.format(search=search, dir=wd))
    acker();
    return acker
ACKer = Threaded.from_function(search_with_ack)
