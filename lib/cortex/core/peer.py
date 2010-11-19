""" cortex.core.peer
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.hds import HDS
from cortex.core.data import API_PORT
from cortex.core.util import report
import datetime
class Peer(HDS):
    """ """

    def __repr__(self):
            port = str(getattr(self,'port','00'))
            addr = getattr(self,'addr','0')
            return 'Peer@' + str(addr) + ':' + str(port)


    def lazy_api(self):
        """ just in time! """
        class DynamicApiProxy(object):
            """ DynamicApiProxy: lazy access to the api"""
            def __getattr__(dap,var):
                """ DynamicApiProxy: lazy access to the api"""
                def fxn(*args, **kargs):
                    """ return a handle on the real function,
                         now that we've been given it's name."""
                    self.eager_api(var, *args, **kargs)
                return fxn

        return DynamicApiProxy()

    api=property(lazy_api)

    @property
    def _proxy(self):
        """ obtain proxy for this peer: a handle on a remote api """
        from txjsonrpc.netstring.jsonrpc import Proxy
        report('dialing peer={addr}::{port}'.format(addr=self.addr,port=API_PORT))
        proxy = Proxy(self.addr, API_PORT)
        return proxy

    @property
    def age(self):
        """ time since last successful connection """
        if hasattr(self,'_last_connection'):
            return datetime.datetime.now() - self._last_connection
        else:
            return datetime.datetime(1800,1,1)

    def _log_last_connection(self, result):
        """ the most basic success callback, last_connection is the minimum
            that will be registered when the api is called.
        """
        self._last_result     = result
        self._last_connection = datetime.datetime.now()

    def eager_api(self, name, *args, **kargs):
            """ the real api, spoken thru a jsonrpc client,
                 to a remote jsonrpc server
            """
            report('dialing@{name}'.format(name=name), args)
            return self._proxy.callRemote(name, *args, **kargs).addCallbacks(self._log_last_connection, self._report_err)

    def _report_err(self, failure):
        """ """
        report('failure in peer',dict(self=self, type=failure.type, value=failure.value, tb=failure.tb))


        #failure.printTraceback()
class PeerManager(Manager):
    """
        Example usage:

          peerMan = PeerManager()
          bob     = peerMan.register('bob',**bob_attributes)
          bob.api.load_service('beacon')

    """

    asset_class = Peer
    def printValue(self, value): report("Result:", str(value))
    def printError(self, error): report('error', error)
    def __iter__(self):
        """ dumb proxy """
        return Manager.__iter__(self)
PEERS=PeerManager()
