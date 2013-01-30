""" cortex.services.linda

    TODO: use reactorrecursion properly
"""

from cortex.services import Service
from cortex.core.ground import Memory
from cortex.core.util import report, report_if_verbose
from cortex.mixins import PersistenceMixin

class Linda(Service):
    """ Linda Service:
          start:
          stop:
    """
    period = 5
    def _post_init(self):
        """ instantiate and back-link """
        Memory.universe = self.universe
        self.universe.ground = Memory(self)

    def clean(self):
        self.universe.ground.clean()

    def iterate(self):
        """ placeholder """
        self.clean()
        self.universe.reactor.callLater(self.period, self.iterate)

    def start(self, universe=True):
        """ placeholder for invoking lindypy multiprocessing,
            for now we just use the underlying datastructures.
        """
        #Service.start(self)
        super(Linda, self).start()
        report_if_verbose("Starting linda tuplespace")
        self.universe.reactor.callLater(self.period, self.iterate)

    def stop(self):
        """ """
        super(Linda, self).stop()
        self.universe.ground.shutdown()
        report_if_verbose("Stopped linda tuplespace")
