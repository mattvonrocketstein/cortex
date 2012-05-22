""" cortex.mixins.local_queue
"""

import Queue
from Queue import Empty as QueueEmpty

class LocalQueue:
    """ TODO: parametrize 'event_q' name
    """
    def __len__(self):
        return self.event_q.qsize()

    def init_q(self):
        """ """
        self.event_q = Queue.Queue()

    def push_q(self, *args, **kargs):
        """ """
        return self.event_q.put([args, kargs])

    def pop_q(self):
        """ """
        try:
            return self.event_q.get(block=False)
        except QueueEmpty:
            pass
