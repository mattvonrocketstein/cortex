""" cortex.services.nmap

"""

import time
import nmap

from cortex.core.util import report
from cortex.services import Service

class Mapper(Service):
    """ Stub Service:
        start: brief description of service start-up here
        stop:  brief description service shutdown here
    """
    def callback_result(self, host, **scan_result):
        """ """
        report('cback', host, **scan_result)

    def print_error(self, *errors):
        """ """
        for x in errors:
            pass # choose any errors to ignore and remove them
        report('error_handler for name resolution', str(errors) )

    def stop(self):
        """ """
        Service.stop(self)
        report('Custom stop for', self)

    def start(self):
        """ start is a function, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """
        Service.start(self)
        nma = nmap.PortScannerAsync()
        def foo(*args, **kargs):
            print kargs or "FOOOOOO"
            host    = args[0]
            results = args[1]
            host_up = results['scan'][host]['status']['state']

            peer_metadata = dict( results = results, # verbose, directly from python-nmap
                                  address = host,    #
                                  alive   = host_up, #
                                  )
            peerMan = self.universe.peers
            report('got peerman',peerMan)

            report('stored in peermap', peerMan.register(host, **peer_metadata),peerMan[host])
            #self.universe.reactor.callLater(300,self.start)

            #print args, kargs
            #self.callback_result(*args, **kargs)
        nma.scan(hosts='10.0.2.15', arguments='-sP', callback=foo)

    def play(self):
        """ stubbed out although services should override
            usually override "start" and not "play" """
        return Service.play(self)
