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

NOT_FOUND_T = 'NOTFound'
port_range = '-'.join([str(p) for p in CORTEX_PORT_RANGE])

def scan2port(scan):
    """ """
    report('scan2', **scan)

class Mapper(Service):
    """ Stub Service:
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """

    def discovery(self, postoffice, pickled_data, **kargs):
        """ will be called by the postoffice, with type PEER_T
        """
        data = simplejson.loads(pickled_data)
        name = data['addr']
        report('registering peer', name,data)
        self.universe.peers.register(name, **data)

    def iterate(self, host):
        """ """
        (self.universe|'postoffice').subscribe(PEER_T, self.discovery)
        scan_data = nmap.PortScanner().scan(host, port_range,'--system-dns')['scan']
        self.last_scan = scan_data
        for addr in scan_data:
            peer_metadata = { 'is_alive'  : scan_data[addr]['status']['state'],
                              'raw_scan'  : scan_data,
                              #'port'      : scan2port(scan_data[addr]),
                              'host'      : scan_data[addr]['hostname'],
                              'addr'      : addr
                            }
            if 'tcp' in scan_data[addr]:
              port_aspect = {
                              'raw_ports' : scan_data[addr]['tcp'],
                              'ports'     : scan_data[addr]['tcp'].keys(),
                              'port'      : scan_data[addr]['tcp'].keys() and \
                                            scan_data[addr]['tcp'].keys()[0],
                            }
            else:
              port_aspect = {'port':NOT_FOUND_T}

            peer_metadata.update(port_aspect)
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

    def play(self):
        """ stubbed out although services should override
            usually override "start" and not "play" """
        return Service.play(self)
