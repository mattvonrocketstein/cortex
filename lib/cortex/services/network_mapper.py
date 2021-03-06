""" cortex.services.network_mapper

      a wrapper around nmap for simplistic peer-discovery

"""

import copy
import nmap, simplejson

from cortex.core.util import report
from cortex.services import Service
from cortex.core.data import PEER_T, LOOPBACK_HOST
from cortex.core.data import CORTEX_PORT_RANGE
from cortex.util.decorators import constraint

NOT_FOUND_T = 'NOTFound'
port_range  = '-'.join([str(p) for p in CORTEX_PORT_RANGE])
from channel import declare_callback

class Mapper(Service):
    """ NMap Service:
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """
    class Meta:
        """ NOTE: mentioning a channel in subscriptions always
                  means it will be created if it does not exist.
        """
        subscriptions = {PEER_T: 'discovery'}

    def discovery(self, peer_data, **kwargs):
        """ will be called by the postoffice, with type PEER_T
        """
        data = peer_data
        name = data['host'] + ':' + str(data['port'])
        self.universe.peers.register(name, **data)

    def iterate(self, host):
        """ """
        local_api_port = (self.universe|'api').port
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
                    #(self.universe|'postoffice').publish_json(PEER_T, metadata)
                    (self.universe|'postoffice').peers(metadata)

            else:
                port_aspect = { 'port' : NOT_FOUND_T }
                peer_metadata.update(port_aspect)
                (self.universe|'postoffice').peers(peer_metadata)
            self.universe.reactor.callLater(10, lambda: self.iterate(host))
    scan = iterate

    @constraint(boot_first='postoffice api'.split())
    def start(self):
        """ TODO:
              it'd be nice to use the asynchronous portscanner but this:
                 >>> nmap.PortScannerAsync().scan('127.0.0.1','10-100',
                                                  '--system-dns',
                                                  callback=foo)
               fails with:
                 PortScannerError:
                   'mass_dns: warning Unable to determine any DNS servers.
        """
        Service.start(self) # can't call super?
        host = getattr(self, 'scan_host', LOOPBACK_HOST)
        self.universe.reactor.callLater(1, lambda: self.iterate(host))
