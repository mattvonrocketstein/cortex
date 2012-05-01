""" cortex.services.api

      This service publishes cortex.core.api via json-rpc.
"""


from txjsonrpc.netstring import jsonrpc
from twisted.internet.error import CannotListenError

from cortex.core.util import report, console
from cortex.core import api as _api
from cortex.services import Service
from cortex.util.decorators import constraint
from cortex.core.data import CORTEX_PORT_RANGE

PORT_START,PORT_FINISH = CORTEX_PORT_RANGE

def wrap(func):
    """ by default the functions will get the API service object as
        the first argument, but functions in cortex.core.api are not
        designed that way (since they are used in node-def parsing,
        the TUI, etc etc).  we need to knock that argument off, and
        assuming that it's always there and always unnecessary should
        be totally safe in this context.
    """
    def newf(*args, **kargs):
        return func(*args[1:], **kargs)
    return newf

def api_wrapper(name="ApiWrapper", bases=(jsonrpc.JSONRPC, object),
                _dict= lambda: _api.publish()):
    """ """

    # if _dict is not a dict then it should be a callable that returns one.
    if hasattr(_dict, '__call__'):
        _dict = _dict()

    # build a test for whether the given name is callable
    # TODO: use NSPart here
    test    = lambda k: hasattr(_dict[k], '__call__') and not k.startswith('_')

    @classmethod
    def _update_api_wrapper(kls):
        """ induces this class to replace itself with a fresher copy.
            this is called when the api is augmented with api.contribute()
            TODO: doesn't need to be in the wrapper.. move back into
            api service.
        """
        report('recomputing the api wrapper')
        (_api.universe|'api').factory.protocol = api_wrapper()


    # wrap the whole namespace we were passed in..
    #  just maps to a different name if item is callable
    wrapped = dict([ ['jsonrpc_' + k,
                      wrap(_dict[k]) ]  for k in _dict if test(k)])
    wrapped.update(_update_api_wrapper=_update_api_wrapper)
    report('publishing', _dict.keys())
    return type(name, bases, wrapped)

#Dynamically build one of the subclasses from the core API definitions
ApiWrapper = api_wrapper()

class API(Service):
    """ API Service:
         publishes the cortex api via jsonRPC

           start:
           stop:
    """
    def augment_with(self, **namespace):
        """ dynamically increase the (json) published api
            using <namespace>

            TODO: define an api-contribute-signal which this
                  service and the terminal service both respond to.
        """
        _api.contribute(**namespace)
        ApiWrapper._update_api_wrapper()
        #for name,value in namespace.items():
        #    assert hasattr(value, '__call__'), "value added to api must be callable"
        #    name = 'jsonrpc_' + name
        #    setattr(ApiWrapper, name, value)
        #return namespace
    contribute = augment_with

    def __init__(self, *args, **kargs):
        from cortex.core.util import getcaller
        report(str(getcaller()))
        self.port = kargs.pop('port', None)
        kargs.update(name='API')
        super(Service,self).__init__(*args, **kargs)
        from cortex.core import api

    def _post_init(self):
        """ """
        pass

    def stop(self):
        """ """
        super(API,self).stop()
        report('the API Service Dies.')

    @constraint(boot_first='gui terminal'.split())
    def start(self):
        """ TODO: ^^ currently only the last constriant is used"""
        super(API, self).start()
        self.factory = jsonrpc.RPCFactory(ApiWrapper)
        count   = self.port or PORT_START
        while count!= PORT_FINISH:
            try:
                # enables system.listMethods method, etc
                self.factory.addIntrospection()
                self.universe.reactor.listenTCP(count, self.factory)
            except CannotListenError:
                count += 1
            else:
                self.port = count
                return self

        return ERROR_T
