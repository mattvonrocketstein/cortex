""" cortex.agents.workers

      Generic agents that deal with doing work, handling tasks
"""
import time, itertools

from cortex.core.agent import Agent
from cortex.core.util import report

class TaskIterator(Agent):
    """ Example usage:

          Run two tasks alternately forever
            >>> TaskIterator(delay=1, tasks=[task1, task2])
    """
    def _post_init(self, delay=1, tasks=[], **kargs):
        """ """
        self.tasks = itertools.cycle(tasks)
        self.delay = delay

    def iterate(self):
        """ """
        task = self.tasks.next()
        task()
        self.universe.reactor.callLater(1, self.iterate)
