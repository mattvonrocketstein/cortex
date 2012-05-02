""" cortex.services.search

      a search service

      TODO: have ACKer instances removed from search.agents automatically when complete
      TODO: make 'bus' less special, parametrizing it somehow
      TODO: make google search service, optionally using domain names
      TODO: make wikipedia search service
      TODO: stop using UUID, key on search term and disallow multiple running simultaneously
      TODO: result caching?
      TODO: demote this from a service.  (then it will be guaranteed to boot after all services)
      TODO: start's first constraint is overwritten actually, but is implied by second anyway
      TODO: report inconsistent constraints: if bootfirst is mentioned but not honored fault()
"""
import os
import json
from channel import Channel

from cortex.core.util import report, uuid
from cortex.services import Service
from cortex.mixins.flavors import Threaded
from cortex.util.decorators import constraint
from cortex.core.agent.manager import AgentManager
from cortex.core.ground import Memory
from .util import search_with_ack, search_with_google

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

    @constraint(boot_first='api postoffice'.split())
    def start(self):
        """ <start> is an operation, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """
        Service.start(self) # TODO: why not super() ?
        self.mem = Memory(self, name='SearchStore')
        poffice = (self.universe|'postoffice')
        (self.universe|'api').contribute(goog=self.google)
        (self.universe|'api').contribute(ack=self.ack)

        def getter(name):
            tpl = (name, object)
            out = self.mem.get(tpl)
            key, data = out
            data = json.loads(data)
            return data
        (self.universe|'api').contribute(get=getter)

        self.bus = Channel.search_bus
        self.bus.bind(poffice)
        self.bus.subscribe(self.search_callback)
        GGLer.bind_result_bus(self.bus)
        ACKer.bind_result_bus(self.bus)

    def google(self, query):
        u = uuid()
        self(GGLer, name='Phase1:internet:' + u, search=search, _id=u,)
        return dict(callback='get("{0}")'.format(u))

    def ack(self, search, wd=os.getcwd()):
        u = uuid()
        self(ACKer, name='Phase1:VeryLocal:'+u,_id=u, wd=wd, search=search)
        return dict(callback='get("{0}")'.format(u))

    def search_callback(self, results, **kargs):
        msg = 'Searcher {0} finished, unpacked {1} results total.  top {2}'
        report(msg.format('(unknown)', len(results), MAX_RESULTS))
        _results = getattr(results, 'weighted', results)
        report.pprint(_results[:MAX_RESULTS])
        self.results = results
        tpl = (results.id, json.dumps(_results))
        self.mem.add(tpl)

GGLer = Threaded.from_function(search_with_google)#, return_bus=self.bus)
ACKer = Threaded.from_function(search_with_ack)#, return_bus=self.bus)
