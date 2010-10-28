""" cortex.services.beacon
"""

from cortex.core.util import report
from cortex.core.services import Service

class Beacon(Service):
    """ Beacon Service:
          start:
          stop:
    """

    def _post_init(self):
        self.is_stopped = False

    def stop(self):
        """ """
        self.is_stopped = True

    def beacon(self):
        if not self.is_stopped:
            self.universe.reactor.callLater(1, self.beacon)
        print " blip "

    def play(self):
        self.universe.reactor.callLater(1,self.beacon)
        return self
