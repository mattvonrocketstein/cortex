""" cortex.core.peer
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.hds import HDS
from cortex.core.data import API_PORT
from cortex.core.util import report

class Peer(HDS):
    """ """

    def __repr__(self):
            port = str(getattr(self,'port','00'))
            addr = getattr(self,'addr','0')
            return 'Peer@' + str(addr) + ':' + str(port)

    def api(self, name, *args):
            """ a jsonrpc client, to a remote jsonrpc server

                  TODO: make this return an HDS that coerces values JIT
            """
            from twisted.internet import reactor
            from txjsonrpc.netstring.jsonrpc import Proxy
            report('dialing peer', self.addr, API_PORT)
            report('using', name, args)
            #raise Exception,self.addr
            proxy = Proxy(self.addr, API_PORT)
            #return proxy
            return proxy.callRemote(name, *args).addCallbacks(report,self.report_err)

    def report_err(self,failure):
        #failure.raiseException()
        failure.printTraceback()
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
