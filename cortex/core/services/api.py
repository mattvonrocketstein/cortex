""" cortex.core.services.api

      This service publishes the api via json-rpc
"""


from cortex.core.util import report, console
from cortex.core.services import Service

from twisted.internet import reactor
#from txjsonrpc.netstring.jsonrpc import Proxy
from twisted.application import service, internet
from txjsonrpc.netstring import jsonrpc
from peak.util.imports import lazyModule
from cortex.core.api import publish #api = lazyModule('')

def api_wrapper(name="ApiWrapper",
                bases=(object,),
                _dict= lambda: publish()):

    # if _dict is not a dict then it should be a callable that returns one.
    if hasattr(_dict,'__call__'):
        _dict=_dict()

    # build a test for whether the given name is callable
    test    = lambda k: hasattr(_dict[k], '__call__')

    # wrap the whole namespace we were passed in..
    #  just maps to a different name if item is callable
    wrapped = dict([['jsonrpc_' + k, _dict[k]] for k in _dict if test(k)])

    return type(name,bases,wrapped)

#Dynamically build one of the subclasses from the core API definitions
ApiWrapper = api_wrapper(bases=(jsonrpc.JSONRPC,object),)

class API(Service, ApiWrapper):
    """ API Service:
         publishes the cortex api via jsonRPC

           start:
           stop:
    """
    def __init__(self,*args, **kargs):
        Service.__init__(self, *args, **kargs)
        #jsonrpc.JSONRPC
        ApiWrapper.__init__(self)
        from cortex.core import api

    def _post_init(self):
        """ """
        pass

    def stop(self):
        """ """
        super(API,self).stop()
        report('the API Service Dies.')

    def start(self):
        """ """
        factory = jsonrpc.RPCFactory(API)
        factory.addIntrospection()
        self.universe.reactor.listenTCP(7080,factory)