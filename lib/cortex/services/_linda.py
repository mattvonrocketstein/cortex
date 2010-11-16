""" cortex.services.linda
"""

import re, pickle
import datetime

from socket import socket

from cortex.services import Service
from cortex.core.ground import Memory
from cortex.core.util import report, console
from cortex.core.atoms import PersistenceMixin

class Linda(Service):
    """ Linda Service:
          start:
          stop:
    """

    def _post_init(self):
        """ """
        self.universe.ground = Memory(self)

    def monitor(self):
        """ """
        pass #self.universe.reactor.callLater(1, self.monitor)

    def start(self, universe=True):
        """ """
        Service.start(self)
        report("Starting linda tuplespace")
        self.universe.reactor.callLater(1, self.monitor)

    def stop(self):
        """ """
        super(Linda, self).stop()
        self.universe.ground.shutdown()
        report("Stopped linda tuplespace")
