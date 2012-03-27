""" cortex.core.peer
"""
import datetime

from cortex.core.agent import Agent as Node
from cortex.core.manager import Manager
from cortex.core.hds import HDS
from cortex.core.data import API_PORT
from cortex.core.util import report

class _Peer(object):
    """ an abstraction representing a generic peer
    """
    def __repr__(self):
        port = str(getattr(self,'port','00'))
        addr = getattr(self,'addr','0')
        return 'Peer@' + str(addr) + ':' + str(port)

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

    def _report_err(self, failure):
        """ """
        report('failure in peer',dict(self=self, type=failure.type, value=failure.value, tb=failure.tb))
        #failure.printTraceback()

    @property
    def _cortex(self):
        c = CortexPeer()
        import copy
        c.addr=self.addr
        c.host=self.host
        return c
class Peer(_Peer,HDS): pass

class gah(object):
    def __init__(self,callabl):
        self.callable=callabl

    def __call__(self, *args, **kargs):
        return self.callable(*args, **kargs)

class CortexPeer(_Peer):
    """ abstraction representing a peer that speaks cortex """

    def __getattr__(self,x):
        #if isinstance(out, HDS):
        return gah(lambda *args, **kargs: self._eager_api(x, *args,**kargs))
        #return out

    @staticmethod
    def factory(fxn,x):
        class xx(object):
            def __call__(self, *args, **kargs):
                return fxn(x, *args, **kargs)
        return xx()

    def _lazy_api(self):
        """ just in time! """
        class DynamicApiProxy(object):
            """ DynamicApiProxy: lazy access to the api """
            def __getattr__(dap,var):
                """ DynamicApiProxy: lazy access to the api """
                def fxn(*args, **kargs):
                    """ return a handle on the real function,
                         now that we've been given it's name. """
                    return self._eager_api(var, *args, **kargs)
                return fxn
        return DynamicApiProxy()
    api = property(_lazy_api)

    @property
    def _proxy(self):
        """ obtain proxy for this peer: a handle on a remote api """
        from txjsonrpc.netstring.jsonrpc import Proxy
        #report('dialing peer={addr}::{port}'.format(addr=self.addr,port=API_PORT))
        proxy = Proxy(self.addr, self.port)
        return proxy

    def _eager_api(self, name, *args, **kargs):
        """ the real api, spoken thru a jsonrpc client,
            to a remote jsonrpc server
        """
        report('dialing@{name}'.format(name=name), args, kargs)
        return self._proxy.callRemote(name, *args,
                                      **kargs).addCallbacks(self._log_last_connection,
                                                                         self._report_err)

class PeerManager(Manager):
    """
        Example usage:
          >>> peerMan = PeerManager()
          []
          >>> bob     = peerMan.register('bob',port=1337,host='AAAA',**bob_attributes)
          Peer@AAAA:1337
          >>> print peerMan
          ['AAAA']
          >>> repr(peerMan)
          manager(['AAAA'])
          >>> peerMan.bob
          Peer@AAAA:1337
          >>> peerMan.bob
          Peer@AAAA:1337
          >>> bob.api.load_service('beacon')

    """
    asset_class = CortexPeer
    def update(self, host='localhost'):
        """ (potentially) update peer list by (re)scanning <host>

             .. it feels kind of weird putting this method here, but
             being able to type peers.update() feels so right..

             Assumptions: "mapper" service is enabled
        """
        self.universe.services['mapper'].obj.scan(host)

    def __getattr__(self,name):
        """ allows for doing peers.localhost """
        ogetattr = object.__getattribute__
        mgetattr = Manager.__getattribute__
        for key in ogetattr(self,'keys')():
            peer = ogetattr(self, '__getitem__')(key)
            if name == peer.host:
                return peer
        return mgetattr(self,name)

    def post_registration(self, peer):
        """ post_registration hook:
             (called by Manager.register when present) """
        #report('sending peer event')
        (self.universe|'postoffice').event(peer)

    def printValue(self, value):
        if value:
            report("Result:", str(value))
    def printError(self, error):
        if error:
            report('error', error)
    def __iter__(self):
        """ dumb proxy """
        return Manager.__iter__(self)

# A cheap singleton
PEERS = PeerManager()
