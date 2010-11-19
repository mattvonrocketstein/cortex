""" cortex.services.nmap
"""

import time
import nmap
import simplejson

from cortex.core.util import report
from cortex.services import Service
from cortex.core.peer import Peer
from cortex.core.data import PEER_T
from cortex.core.data import CORTEX_PORT_RANGE

port_range = '-'.join([str(p) for p in CORTEX_PORT_RANGE])

class Mapper(Service):
    """ Stub Service:
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """

    def discovery(self, postoffice, pickled_data, **kargs):
        """ """
        data = simplejson.loads(pickled_data)
        name = data['addr']
        report('registering peer', name)
        self.universe.peers.register(name, **data)

    def iterate(self, host):
        """ """
        (self.universe|'postoffice').subscribe(PEER_T, self.discovery)
        scan_data = nmap.PortScanner().scan(host, port_range,'--system-dns')['scan']
        self.last_scan = scan_data
        for addr in scan_data:
            peer_metadata = { 'is_alive'  : scan_data[addr]['status']['state'],
                              'host'      : scan_data[addr]['hostname'],
                              'addr'      : addr }
            peer = peer_metadata
            (self.universe|'postoffice').publish_json(PEER_T, peer)

    def start(self):
        """ i'd like to use the asynchronous portscanner but this
              scan_data = nmap.PortScannerAsync().scan('127.0.0.1','10-100','--system-dns',callback=foo)

            fails with:
              PortScannerError: 'mass_dns: warning Unable to determine any DNS servers.
        """
        Service.start(self)
        host = '127.0.0.1'
        self.universe.reactor.callLater(1, lambda: self.iterate(host))
        #nma_kargs = dict(hosts='10.0.2.15', arguments='--system-dns', callback=foo)
        #self.universe.reactor.callLater(1, lambda: nma.scan(**nma_kargs))

    def play(self):
        """ stubbed out although services should override
            usually override "start" and not "play" """
        return Service.play(self)
