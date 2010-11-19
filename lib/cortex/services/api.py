""" cortex.services.api

      This service publishes the api via json-rpc

class Test(jsonrpc.JSONRPC):

    FAILURE = 666
    NOT_FOUND = jsonrpclib.METHOD_NOT_FOUND
    SESSION_EXPIRED = 42


class Test:
    def setUp(self):
        jsonrpc = Test()
        addIntrospection(jsonrpc)
        self.p = reactor.listenTCP(
            0, server.Site(jsonrpc),interface="127.0.0.1")
        self.port = self.p.getHost().port

    def testListMethods(self):

        def cbMethods(meths):
            meths.sort()
            self.failUnlessEqual(
                meths,
                ['add', 'complex', 'defer', 'deferFail',
                 'deferFault', 'dict', 'fail', 'fault',
                 'none', 'pair', 'system.listMethods',
                 'system.methodHelp',
                 'system.methodSignature'])

        d = self.proxy().callRemote("system.listMethods")
        d.addCallback(cbMethods)
        return d

    def testMethodHelp(self):
        inputOutputs = [
            ("defer", "Help for defer."),
            ("fail", ""),
            ("dict", "Help for dict.")]

        dl = []
        for meth, expected in inputOutputs:
            d = self.proxy().callRemote("system.methodHelp", meth)
            d.addCallback(self.assertEquals, expected)
            dl.append(d)
        return defer.DeferredList(dl, fireOnOneErrback=True)

"""


from cortex.core.util import report, console
from cortex.services import Service
#from txjsonrpc.netstring.jsonrpc import Proxy
from twisted.internet import reactor, defer
from twisted.application import service, internet
from txjsonrpc.netstring import jsonrpc
from peak.util.imports import lazyModule
#from txjsonrpc.jsonrpc import addIntrospection

from cortex.core.api import publish
from cortex.core.data import API_PORT


#DEFAULT_PORT=7080

def api_wrapper(name="ApiWrapper", bases=(object, jsonrpc.JSONRPC,), _dict= lambda: publish()):

    # if _dict is not a dict then it should be a callable that returns one.
    if hasattr(_dict,'__call__'):
        _dict=_dict()

    # build a test for whether the given name is callable
    test    = lambda k: hasattr(_dict[k], '__call__')

    # wrap the whole namespace we were passed in..
    #  just maps to a different name if item is callable
    wrapped = dict([['jsonrpc_' + k, _dict[k]] for k in _dict if test(k)])

    return type(name, bases, wrapped)

#Dynamically build one of the subclasses from the core API definitions
#ApiWrapper = api_wrapper(bases=(jsonrpc.JSONRPC,object),)
from txjsonrpc import jsonrpclib
class API(Service, jsonrpc.JSONRPC):#, ApiWrapper):
    """ API Service:
         publishes the cortex api via jsonRPC

           start:
           stop:
    """
    FAILURE = 666
    NOT_FOUND = jsonrpclib.METHOD_NOT_FOUND
    SESSION_EXPIRED = 42

    def jsonrpc_add(self, a, b):
        """
        This function add two numbers.
        """
        # The doc string is part of the test.
        return a + b

    jsonrpc_add.signature = [['int', 'int', 'int'],
                            ['double', 'double', 'double']]

    def jsonrpc_pair(self, string, num):
        """
        This function puts the two arguments in an array.
        """
        # The doc string is part of the test.
        return [string, num]

    jsonrpc_pair.signature = [['array', 'string', 'int']]

    def jsonrpc_defer(self, x):
        """
        Help for defer.
        """
        # The doc string is part of the test.
        return defer.succeed(x)

    def jsonrpc_deferFail(self):
        return defer.fail(TestValueError())

    def jsonrpc_fail(self):
        # Don't add a doc string, it's part of the test.
        raise TestRuntimeError

    def jsonrpc_fault(self):
        return jsonrpclib.Fault(12, "hello")

    def jsonrpc_deferFault(self):
        return defer.fail(jsonrpclib.Fault(17, "hi"))

    def jsonrpc_complex(self):
        return {"a": ["b", "c", 12, []], "D": "foo"}

    def jsonrpc_dict(self, map, key):
        return map[key]

    def jsonrpc_none(self):
        return "null"

    def _getFunction(self, functionPath):
        try:
            return jsonrpc.JSONRPC._getFunction(self, functionPath)
        except jsonrpclib.NoSuchFunction:
            if functionPath.startswith("SESSION"):
                raise jsonrpclib.Fault(
                    self.SESSION_EXPIRED, "Session non-existant/expired.")
            else:
                raise

    jsonrpc_dict.help = 'Help for dict.'


    def __init__(self, *args, **kargs):
        self.port = kargs.pop('port', API_PORT)
        Service.__init__(self,*args, **kargs)
        #jsonrpc.JSONRPC(self)
        #from txjsonrpc.jsonrpc import addIntrospection
        from txjsonrpc.web.jsonrpc import addIntrospection
        self.subHandlers = {}
        addIntrospection(self)

    def proxy(self):
        #return jsonrpc.Proxy("http://127.0.0.1:%d/" % self.port)
        from txjsonrpc.netstring.jsonrpc import Proxy
        proxy = Proxy(self.interface, API_PORT)
        return proxy

    #def proxy(self):
    #    return jsonrpc.Proxy("http://127.0.0.1:%d/" % self.port)

    def testMethodSignature(self):
        inputOutputs = [
            ("defer", ""),
            ("add", [['int', 'int', 'int'],
                     ['double', 'double', 'double']]),
            ("pair", [['array', 'string', 'int']])]

        dl = []
        for meth, expected in inputOutputs:
            d = self.proxy().callRemote("system.methodSignature", meth)
            d.addCallback(report, expected)
            dl.append(d)
        return defer.DeferredList(dl, fireOnOneErrback=True)

    #def __init__(self, *args, **kargs):
    #    
    #    Service.__init__(self, *args, **kargs)
    #    ##jsonrpc.JSONRPC
    #    ApiWrapper.__init__(self)
    #    from cortex.core import api

    def _post_init(self):
        """ """
        #is this running?

    def stop(self):
        """ """
        super(API,self).stop()
        report('the API Service Dies.')

    def start(self):
        """ """
        #factory = jsonrpc.RPCFactory(API)
        #factory.addIntrospection()
        #addIntrospection(factory)
        self.interface = "127.0.0.1"
        #from txjsonrpc.web import jsonrpc
        from twisted.web import server, static
        self.api_engine = self.universe.reactor.listenTCP(self.port, server.Site(API()),
                                                          interface=self.interface)
        self.port = self.api_engine.getHost().port
        report('started api engine on',self.interface, self.port)
        #self.universe.reactor.listenTCP(self.port, factory)

    def jsonrpc_add(self, a, b):
        """
        This function add two numbers.
        """
        # The doc string is part of the test.
        return a + b

    jsonrpc_add.signature = [['int', 'int', 'int'],
                            ['double', 'double', 'double']]

    def jsonrpc_pair(self, string, num):
        """
        This function puts the two arguments in an array.
        """
        # The doc string is part of the test.
        return [string, num]

    jsonrpc_pair.signature = [['array', 'string', 'int']]

    def jsonrpc_defer(self, x):
        """
        Help for defer.
        """
        # The doc string is part of the test.
        return defer.succeed(x)

    def jsonrpc_deferFail(self):
        return defer.fail(TestValueError())

    def jsonrpc_fail(self):
        # Don't add a doc string, it's part of the test.
        raise TestRuntimeError

    def jsonrpc_fault(self):
        return jsonrpclib.Fault(12, "hello")

    def jsonrpc_deferFault(self):
        return defer.fail(jsonrpclib.Fault(17, "hi"))

    def jsonrpc_complex(self):
        return {"a": ["b", "c", 12, []], "D": "foo"}

    def jsonrpc_dict(self, map, key):
        return map[key]

    def jsonrpc_none(self):
        return "null"

    def _getFunction(self, functionPath):
        try:
            return jsonrpc.JSONRPC._getFunction(self, functionPath)
        except jsonrpclib.NoSuchFunction:
            if functionPath.startswith("SESSION"):
                raise jsonrpclib.Fault(
                    self.SESSION_EXPIRED, "Session non-existant/expired.")
            else:
                raise

    jsonrpc_dict.help = 'Help for dict.'
