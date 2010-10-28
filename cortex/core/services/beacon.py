""" cortex.services.beacon
"""

from cortex.core.util import report
from cortex.core.services import Service

class Beacon(Service):
    """ Beacon Service:
          start:
          stop:
    """
    def beacon(self):
        self.universe.reactor.callLater(1, self.beacon)
        print " blip "

    def play(self):
        self.universe.reactor.callLater(1,self.beacon)
