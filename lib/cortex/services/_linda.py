""" cortex.services.linda
"""

from cortex.services import Service
from cortex.core.ground import Memory
from cortex.core.util import report, console
from cortex.mixins import PersistenceMixin

class Linda(Service):
    """ Linda Service:
          start:
          stop:
    """

    def _post_init(self):
        """ instantiate and back-link """
        Memory.universe = self.universe
        self.universe.ground = Memory(self)

    def monitor(self):
        """ placeholder """
        pass #self.universe.reactor.callLater(1, self.monitor)

    def start(self, universe=True):
        """ placeholder for invoking lindypy multiprocessing,
            for now we just use the underlying datastructures.
        """
        #Service.start(self)
        super(Linda,self).start()
        #report("Starting linda tuplespace")
        self.universe.reactor.callLater(1, self.monitor)

    def stop(self):
        """ """
        super(Linda, self).stop()
        self.universe.ground.shutdown()
        #report("Stopped linda tuplespace")
