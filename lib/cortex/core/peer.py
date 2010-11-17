""" cortex.core.peer
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.hds import HDS
from cortex.core.util import report

class PeerManager(Manager):
    """

        peerMan = PeerManager()
        bob     = peerMan.register('bob',**bob_attributes)

    """

    class asset_class(HDS):
        """ """

        def __str__(self):
            port = str(getattr(self,'port','00'))
            addr = getattr(self,'address','0')
            return 'Peer@' + addr + ':' + port
        __repr__ = __str__

        def api(self, name, *args):
            """ a jsonrpc client, to a remote jsonrpc server

                  TODO: make this return an HDS that coerces values JIT
            """
            from twisted.internet import reactor
            from txjsonrpc.netstring.jsonrpc import Proxy
            proxy = Proxy(self.address, 1337)
            return proxy.callRemote(name, *args).addCallbacks(PeerManager.printValue,
                                                              PeerManager.printError)

    def printValue(self, value): report("Result:", str(value))
    def printError(self, error): report('error', error)
    def __iter__(self):
        """ dumb proxy """
        return Manager.__iter__(self)
PEERS=PeerManager()
