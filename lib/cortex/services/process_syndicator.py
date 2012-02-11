"""
"""

from cortex.core.util import report, console

class ProcessReadSyndication(Service, protocol.ProcessProtocol):
    """ ProcessReaderSyndication Service:
          start:
          stop:
    """

    #protocol.ProcessProtocol.__init__(self)
    def errReceived(self, data):
        report("errReceived! with %d bytes!" % len(data))
        report(data)

    #def inConnectionLost(self):
    #    print "inConnectionLost! stdin is closed! (we probably did it)"

    def outConnectionLost(self):
        """ The child closed their stdout
            now is the time to examine what they wrote """
        report("I saw them write:")
        console.draw_line()
        report(self.data)
        console.draw_line()

    #def errConnectionLost(self):
    #    print "errConnectionLost! The child closed their stderr."

    #def processExited(self, reason):
    #    print "processExited, status %d" % (reason.value.exitCode,)

    def harikari(self):
        """
        """
        self.stop()
        self.universe.leave()

    def processEnded(self, reason):
        #print "processEnded, status %d" % (reason.value.exitCode,)
        report("quitting", reason.value.exitCode)
        self.harikari()
        #self.universe.reactor.stop()

    def outReceived(self, data):
        report('receiving..')
        self.data = self.data + data

    def asdf_sayHello(self):
        for i in range(self.verses):
            self.transport.write("Aleph-null bottles of beer on the wall,\n" +
                                 "Aleph-null bottles of beer,\n" +
                                 "Take one down and pass it around,\n" +
                                 "Aleph-null bottles of beer on the wall.\n")
        self.transport.closeStdin() # tell them we're done

    def connectionMade(self):
        report("connectionMade!",type(self.transport))
        if hasattr(self,'sayHello'):
            self.sayHello()

    def start(self):
        report("starting")
        reactor.spawnProcess(self, '/home/matt/code/cortex/node/bin/linda_server')
