""" cortex.services.api

      This service publishes the api via json-rpc
"""


from cortex.core.util import report, console
from cortex.util.decorators import constraint
from cortex.services import Service

from twisted.internet import reactor #from txjsonrpc.netstring.jsonrpc import Proxy
from twisted.application import service, internet
from txjsonrpc.netstring import jsonrpc
from peak.util.imports import lazyModule

from cortex.core.api import publish
from cortex.core.data import CORTEX_PORT_RANGE

PORT_START,PORT_FINISH = CORTEX_PORT_RANGE

def api_wrapper(name="ApiWrapper", bases=(jsonrpc.JSONRPC, object,), _dict= lambda: publish()):
    """ """

    # if _dict is not a dict then it should be a callable that returns one.
    if hasattr(_dict,'__call__'):
        _dict = _dict()

    # build a test for whether the given name is callable
    test    = lambda k: hasattr(_dict[k], '__call__') and not k.startswith('_')

    # wrap the whole namespace we were passed in..
    #  just maps to a different name if item is callable
    wrapped = dict([['jsonrpc_' + k, _dict[k]] for k in _dict if test(k)])
    report('publishing',_dict.keys())
    return type(name, bases, wrapped)

#Dynamically build one of the subclasses from the core API definitions
ApiWrapper = api_wrapper(bases=(jsonrpc.JSONRPC,object),)

class API(Service, ApiWrapper):
    """ API Service:
         publishes the cortex api via jsonRPC

           start:
           stop:
    """
    def augment_with(self, **namespace):
        """ dynamically increase the published api
            using <namespace> """
        for name,value in namespace.items():
            assert hasattr(value, '__call__'), "value added to api must be callable"
            name = 'jsonrpc_' + name
            setattr(self, name, value)
        return namespace

    def __init__(self, *args, **kargs):
        self.port = kargs.pop('port', None)
        Service.__init__(self, *args, **kargs)
        ApiWrapper.__init__(self)
        from cortex.core import api

    def _post_init(self):
        """ """
        pass

    def stop(self):
        """ """
        super(API,self).stop()
        report('the API Service Dies.')

    @constraint(boot_first='terminal')
    @constraint(boot_first='gui')
    def start(self):
        """ """

# TODO: unittest like this
#       terminal = (self.universe|'terminal') or \
#                  (self.universe|'gui')
#       assert terminal,"Boot order not working?"
#
        from twisted.internet.error import CannotListenError
        factory = jsonrpc.RPCFactory(API)

        count   = self.port or PORT_START
        while count!= PORT_FINISH:
            try:
                # enables system.listMethods method, etc
                factory.addIntrospection()
                self.universe.reactor.listenTCP(count, factory)
            except CannotListenError:
                count += 1
            else:
                self.port = count
                return self

        return ERROR_T
