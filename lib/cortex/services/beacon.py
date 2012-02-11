""" cortex.services.beacon
"""

from cortex.core.util import report
from cortex.services import Service
from cortex.core.util import report
from cortex.core.data import EVENT_T


BEACON_INTERVAL = 1        # how often to go blip; value is in seconds
BLIP            = " blip " # how exactly to say blip

class Beacon(Service):
    """ Beacon Service
          is a pretty useful tool for debugging things, and one of the simplest
          services imaginable.  It can tell you if the reactor is working, and
          it can be used to test the event-bus.

        Operations:
          <start>: initiates some asynchronous beep-beep-beeping
          <stop>:  makes the beeps go away.
    """

    ROLL_OVER = 1337 # count to this many before starting over.

    def _post_init(self, mode='stdout', **kargs):
        """ """
        self.count = 0
        super(Beacon,self)._post_init(**kargs)
        self.mode = mode

    def stop(self):
        """ """
        super(Beacon,self).stop()
        report("The beacon dies.")

    def beacon(self):
        """ goes !blip """
        self.count = (self.count+1) % Beacon.ROLL_OVER

        if self.mode == 'stdout':
            print BLIP + str(self.count)

        if self.mode == 'postoffice':
            # need some extra setup if postoffice will be used
            if not hasattr(self, 'postoffice'):
                self.postoffice = (self.universe|'postoffice')
            self.postoffice.publish(EVENT_T, BLIP + str(self.count))

        if not self.is_stopped:
            self.universe.reactor.callLater(BEACON_INTERVAL, self.beacon)

    def start(self):
        """
            TODO: self.requires_service('postoffice')
        """
        self.beacon()
