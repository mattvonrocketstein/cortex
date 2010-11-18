""" cortex.services.nmap
"""

import time
import nmap
import simplejson

from cortex.core.util import report
from cortex.core.data import PEER_T
from cortex.services import Service


class Mapper(Service):
    """ Stub Service:
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """

    def discovery(self, postoffice, pickled_data, **kargs):
        """ """
        data = simplejson.loads(pickled_data)
        self.universe.peers.register(data['addr'],**data)

    def iterate(self):
        (self.universe|'postoffice').subscribe(PEER_T, self.discovery)
        scan_data = nmap.PortScanner().scan('127.0.0.1','10-100','--system-dns')['scan']
        self.last_scan = scan_data
        for addr in scan_data:
            peer_metadata = { 'is_alive'  : scan_data[addr]['status']['state'],
                              'host' : scan_data[addr]['hostname'],
                              'addr'      : addr }
            (self.universe|'postoffice').introduce(peer_metadata)

    def start(self):
        """ start is a function, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """

        Service.start(self)

        # this fails with:
        #   PortScannerError: 'mass_dns: warning Unable to determine any DNS servers.
        #scan_data = nmap.PortScannerAsync().scan('127.0.0.1','10-100','--system-dns',callback=foo)#['scan']
        self.universe.reactor.callLater(1, self.iterate)
        #nma_kargs = dict(hosts='10.0.2.15', arguments='--system-dns', callback=foo)
        #self.universe.reactor.callLater(1, lambda: nma.scan(**nma_kargs))

    def play(self):
        """ stubbed out although services should override
            usually override "start" and not "play" """
        return Service.play(self)
