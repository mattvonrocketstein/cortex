""" cortex.services.network_mapper

      a wrapper around nmap for simplistic peer-discovery

"""

import time, copy
import nmap, simplejson

from cortex.core.util import report
from cortex.services import Service
from cortex.core.peer import Peer
from cortex.core.data import PEER_T
from cortex.core.data import CORTEX_PORT_RANGE
from cortex.util.decorators import constraint

NOT_FOUND_T = 'NOTFound'
port_range  = '-'.join([str(p) for p in CORTEX_PORT_RANGE])

class AbstractMapper(Service):
    pass

class Mapper(AbstractMapper):
    """ NMap Service:
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """

    def discovery(self, postoffice, pickled_data, **kargs):
        """ will be called by the postoffice, with type PEER_T
        """
        data = simplejson.loads(pickled_data)
        name = data['host']+':'+str(data['port'])
        self.universe.peers.register(name, **data)

    def iterate(self, host):
        """ """
        local_api_port = (self.universe|'api').port
        (self.universe|'postoffice').subscribe(PEER_T, self.discovery)
        self.port_range = port_range
        scan_data = nmap.PortScanner().scan(host, port_range, '--system-dns')['scan']
        self.last_scan = scan_data
        for addr in scan_data:
            peer_metadata = { 'is_alive'  : scan_data[addr]['status']['state'],
                              'raw_scan'  : scan_data,
                              'host'      : scan_data[addr]['hostname'],
                              'addr'      : addr
                            }
            if 'tcp' in scan_data[addr]:
                port_aspect = {
                    'raw_ports' : scan_data[addr]['tcp'],
                    'ports'     : scan_data[addr]['tcp'].keys(),
                    }

                # one peer per port
                for port in port_aspect['ports']:
                    metadata  = copy.copy(peer_metadata)
                    port_data = copy.copy(port_aspect)
                    port_data.update({'port':port})

                    # if this peer has the port which is used by the API service in *this*
                    #  universe, and if the address is the same as this universe, then
                    #   this host is us!  it gets a special name: "self" accessible as ie
                    #    universe.peers.self from console
                    if (port == local_api_port) and (addr in self.universe.ips):
                        metadata.update({'host':'self'})

                    metadata.update(port_data)
                    (self.universe|'postoffice').publish_json(PEER_T, metadata)

            else:
                port_aspect = { 'port' : NOT_FOUND_T }
                peer_metadata.update(port_aspect)
                (self.universe|'postoffice').publish_json(PEER_T, peer_metadata)
            self.universe.reactor.callLater(10, lambda: self.iterate(host))
    scan = iterate

    @constraint(boot_first='postoffice')
    @constraint(boot_first='api')
    def start(self):
        """ i'd like to use the asynchronous portscanner but this
              scan_data = nmap.PortScannerAsync().scan('127.0.0.1','10-100','--system-dns',callback=foo)

            fails with:
              PortScannerError: 'mass_dns: warning Unable to determine any DNS servers.
        """

        #assert (self.universe|'api').started, 'postoffice isnt started'
        Service.start(self)
        #self._boot_first = ['terminal'] # testing service bootorder csp
        host = getattr(self,'scan_host','127.0.0.1')
        self.universe.reactor.callLater(1, lambda: self.iterate(host))
