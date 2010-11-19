""" cortex.services.beacon
"""
import simplejson as json
from twisted.internet.protocol import DatagramProtocol

from cortex.services import Service
from cortex.core.util import report, console
from cortex.core.universe import Universe

GROUP = '227.3.3.7'
PORT = 31337

class Consumer(DatagramProtocol):
    def __init__(self, universe):
        self.universe = universe

    def startProtocol(self):
        "Called when transport is connected"
        self.transport.joinGroup(GROUP)
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"

    def datagramReceived(self, data, (host, port)):
        try: advert = json.loads(data)
        except json.decoder.JSONDecodeError, e:
            return #Write it off as nouse
        if advert['universe'] == self.universe.name:
            report("Self-advert ignored")
            return

        report("received %s from %s:%d" % (advert, host, port))


class Advertiser(DatagramProtocol):
    def __init__(self, universe, group=GROUP, port=PORT):
        self.universe = universe
        self.group = group
        self.port = port
        self.running = False

    def advertise(self):
        if not self.running:
            report("WARNING", "Trying to advertise while not running")
            return
        report("TODO: Advertising!")
        advert = json.dumps({'universe': self.universe.name,
                             'services': {}
                             })
        print "Writing: %d to %s %s" % (self.transport.write(advert, (self.group, self.port)), self.group, self.port)

        if self.running:
            self.universe.reactor.callLater(3, self.advertise)

    def startProtocol(self):
        self.running = True
        self.transport.joinGroup(self.group).addBoth(lambda *args, **kwargs: report("Join: ", *args, **kwargs))
        self.advertise()

    def stopProtocol(self):
        self.running = False
        self.transport.leaveGroup(self.group).addBoth(lambda *args, **kwargs: report("Join: ", *args, **kwargs))


class MudPee(Service):
    """
    MUlticastuDpPEErdiscovery service
      Will broadcast JSON dicts in the form of
      {
          "universe": "universe_name",

          services: {
              "name": True || {"option1": "value1" ...}
              .
              .
          }
      }

    Operations:
      <start>: initiates service advertisements and listens for them
      <stop>:  Stops the service
    """

    def stop(self):
        """ """
        Service.stop(self)
        report('Stopping MudPee', self)
        self.advertiser.stopListening().addCallback(report)

    def start(self):
        """
        """
        report('Starting MudPee', self)
        advert = Advertiser(Universe)
        self.advertiser = Universe.reactor.listenMulticast(PORT, advert, listenMultiple=True)
        consumer = Consumer(Universe)
        self.consumer = Universe.reactor.listenMulticast(PORT, consumer, listenMultiple=True)
        report("Advertiser:", self.advertiser)
        report("Consumer:", self.consumer)
