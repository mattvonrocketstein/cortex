""" cortex.services.linda """

from cortex.core.util import report, console
from cortex.core.services import Service

from twisted.internet import protocol
from twisted.internet import reactor
import re

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
from socket import socket
#  node/lib/python2.6/site-packages/linda-0.6-py2.6.egg/linda/monitor/pyg_monitor.pyl
#./node/lib/python2.6/site-packages/linda-0.6-py2.6.egg/lib/python2.6/site-packages/linda/monitor/pyg_monitor.pyl

class Linda(Service): #ProcessReadSyndication):
    """ Linda Service:
          start:
          stop:
    """

    def _post_init(self):
        """ """
        self.data = ""

    def start(self):
        """ """
        from lindypy.TupleSpace import TSpace
        self.ts = TSpace()
        ts=self.ts
        ts.add((1,2,3,4))
        ts.add((5,2,3,7))
        ts.add((1,2,3,4,5,6))
        #print ts.get((object,2,3,object))
        #print (1,2,3,4)

        report("Starting linda tuplespace")
        def main():
            #__requires__ = 'linda==0.6'
            #import pkg_resources
            #import linda
            #from linda.server import main
            #try:
            #    main()
            #except IOError,e:
            #    report('socket.error? ',str(e))
            pass
        self.universe.reactor.callInThread(main)


    def stop(self):
        """ """
        super(Linda,self).stop()

    #def start(self):
    #    report("starting")
