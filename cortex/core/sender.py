""" cortex.core.sender
"""

import sys, os
from twisted.protocols.basic import FileSender
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols import basic

class TransferCancelled(Exception):
    """Exception for a user cancelling a transfer"""
    pass

class FileIOClient(basic.LineReceiver):
    """ file sender """
    def __init__(self, path, controller):
        self.path = path
        self.controller = controller

        self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size

        self.result = None
        self.completed = False

        self.controller.file_sent = 0
        self.controller.file_size = self.insize

    def _monitor(self, data):
        self.controller.file_sent += len(data)
        self.controller.total_sent += len(data)

        # Check with controller to see if we've been cancelled and abort
        # if so.
        if self.controller.cancel:
            print 'FileIOClient._monitor Cancelling'
            # Need to unregister the producer with the transport or it will
            # wait for it to finish before breaking the connection
            self.transport.unregisterProducer()
            self.transport.loseConnection()
            # Indicate a user cancelled result
            self.result = TransferCancelled('User cancelled transfer')

        return data

    def cbTransferCompleted(self, lastsent):
        self.completed = True
        self.transport.loseConnection()

    def connectionMade(self):
        self.transport.write('%s\r\n' % (self.insize))
        sender = FileSender()
        sender.CHUNK_SIZE = 2 ** 16
        d = sender.beginFileTransfer(self.infile, self.transport,
                                     self._monitor)
        d.addCallback(self.cbTransferCompleted)

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        print 'FileIOClient:connectionLost\n\t',str(reason)
        self.infile.close()
        if self.completed:
            self.controller.completed.callback(self.result)
        else:
            self.controller.completed.errback(reason)
        reactor.stop()

class FileIOClientFactory(ClientFactory):
    """ file sender factory """
    protocol = FileIOClient

    def __init__(self, path, controller):
        self.path = path
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        print 'buildProtocol'
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p

def transmitOne(path, address='localhost', port=1234, ):
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed


if __name__=='__main__':
    if len(sys.argv)>1:
        arg = sys.argv[1]
    else:
        arg = sys.argv[0]
    x = transmitOne(arg)
    reactor.run()
