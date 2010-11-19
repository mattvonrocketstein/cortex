""" cortex.services.beacon
"""

from cortex.services import Service
from cortex.core.util import report, console
from cortex.core.universe import Universe

from twisted.internet.protocol import DatagramProtocol

GROUP = '227.3.3.7'
PORT = 31337

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
        print "Writing: %d to %s %s" % (self.transport.write("Hello world", (self.group, self.port)), self.group, self.port)

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
    MUlticastDnsPeerdiscovery service
      Will broadcast JSON dicts in the form of
      {
          "name": "universe_name",

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
        report("Advertiser:", self.advertiser)
