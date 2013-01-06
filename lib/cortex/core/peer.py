""" cortex.core.peer
"""
import datetime

from txjsonrpc.netstring.jsonrpc import Proxy

from cortex.core.agent import Agent as Node
from cortex.core.manager import Manager
from cortex.core.hds import HDS
from cortex.core.data import API_PORT
from cortex.core.util import report

class Peer(object):
    """ peer-ish
    """

    @property
    def agent(self):
        if hasattr(self,'_agent'):
            return self._agent
        else:
            autodiscover = [ x for x in self.universe.children() \
                             if getattr(x, 'port', None) == self.port ]
            if autodiscover:
                return autodiscover[0]
            else:
                return None

    def local(self):
        """ boolean for whether this peer is local """
    # hack for ipython tab completion
    def _getAttributeNames(self):
        return []
    trait_names = _getAttributeNames

    def __init__(self, addr=None, port=None):
        self.addr = addr
        self.port = port
        # HACK
        from cortex.core.universe import Universe
        self.universe = Universe

    def mutate_if_cortex(self, failure=None):
        handshake = 'helo'
        potentially = self._cortex
        def success(result):
            if result==handshake:
                for name,peer in self._manager.registry.items():
                    if peer == self:
                        self._manager.registry[name] = potentially
                        #report('replacing myself with something better')
                        break
            else:

                if self.universe.started:
                    report("got an answer back, but it's not the handshake.."+str(result))
        def _failure(whatever):
            report('failed ' + str(whatever))
        potentially.is_cortex(handshake).addCallbacks(success,failure or _failure)

    def __repr__(self):
        port = str(getattr(self, 'port', '00'))
        addr = getattr(self, 'addr', '0')
        return 'Peer@' + str(addr) + ':' + str(port)

    def _log_last_connection(self, result):
        """ the most basic success callback, last_connection is the minimum
            that will be registered when the api is called.

            NB: don't forget to return the result or you'll
                change it for any other callbacks in the chain
        """
        self._last_result     = result
        self._last_connection = datetime.datetime.now()
        return result

    def _report_err(self, failure):
        """ we only want to propogate failures under certain conditions.

            this method is complicated by the fact that peers might be
            created as a result of network-mapper discovery OR stand-alone.
            without a check, the screen clogs with errors during shutdown.
        """
        from twisted.internet.error import ConnectionRefusedError
        if hasattr(self,'_manager'):
            if self.universe.started:
                if failure.type==ConnectionRefusedError:
                    report("Connection Refused: "+str(self))
                    return failure
                else:
                    report('failure in peer',dict(self=self, type=failure.type,
                                                  value=failure.value, tb=failure.tb))
                    return failure

        else:
            return failure
        #failure.printTraceback()

    @property
    def _cortex(self):
        c = CortexPeer()
        c.addr = self.addr
        c.port = self.port
        c.__dict__ = self.__dict__
        return c

class MethodHandle(object):
    def __init__(self,callabl):
        self.callable = callabl

    def __call__(self, *args, **kargs):
        return self.callable(*args, **kargs)


#def ifCortex(peer,):
#    p = Proxy(str(peer.addr), int(peer.port))
#    p.callRemote('echo',3).addCallbacks(report,report)

class CortexPeer(Peer):
    """ abstraction representing a peer that speaks cortex """

    def __getattr__(self,x):
        #if isinstance(out, HDS):
        return MethodHandle(lambda *args, **kargs: self._eager_api(x, *args,**kargs))
        #return out
    def __repr__(self):
        return super(CortexPeer,self).__repr__().replace('Peer@','CortexPeer@')

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
        #report('dialing peer={addr}::{port}'.format(addr=self.addr,port=API_PORT))
        proxy = Proxy(self.addr, self.port)
        return proxy

    def _eager_api(self, name, *args, **kargs):
        """ the real api, spoken thru a jsonrpc client,
            to a remote jsonrpc server
        """
        #report('dialing@{name}'.format(name=name), args, kargs)
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
    asset_class = Peer

    def update(self, host='localhost'):
        """ (potentially) update peer list by (re)scanning <host>

             .. it feels kind of weird putting this method here, but
             being able to type peers.update() feels so right..

             Assumptions: "mapper" service is enabled
        """
        (self.universe|'mapper').scan(host)

    def __getattr__(self,name):
        """ allows for doing peers.localhost """
        ogetattr = object.__getattribute__
        mgetattr = Manager.__getattribute__
        for key in ogetattr(self,'keys')():
            peer = ogetattr(self, '__getitem__')(key)
            if name == peer.addr:
                return peer
        return mgetattr(self,name)

    def post_registration(self, peer):
        """ post_registration hook:
             (called by Manager.register when present)
        """
        # note: event_T not peer_T
        peer._manager = self
        (self.universe|'postoffice').event(peer)

        peer.mutate_if_cortex()
        return peer

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
