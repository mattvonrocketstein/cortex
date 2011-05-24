""" cortex.demos.philosophers:
      Demo of agent-oriented approach for solving dining philosophers.

    See also:
      cortex.demos.philosophers.rosetta: reference implementation
      http://en.wikipedia.org/wiki/Dining_philosophers_problem

"""

from cortex.mixins.flavors import ThreadedAgent
from cortex.demos.philosophers.rosetta import Philosopher as RosettaPhilosopher

class Philosopher(ThreadedAgent, RosettaPhilosopher):
    """ This class is a thin wrapper around the rosetta example

        It serves as a demo for how to "agentify" any random threaded code.

        NOTE: RosettaPhilosopher.run() is not used! run() is inherited from ThreadedAgent
    """

    def __repr__(self):
        return "<{name}>".format(name=self.name)

    def _post_init(self, forkOnLeft=None, forkOnRight=None):
        """ replacement for rosetta's philosopher.__init__ """
        self.forkOnLeft = forkOnLeft
        self.forkOnRight = forkOnRight

    def run_primitive(self):
        """ replacement for rosetta's philosopher.run(), that loop is essentially
            already abstracted upwards into ThreadedAgent.run()
        """
        self.wait() # without arguments, blocks for one second
        print('%s is hungry.' % self.name)
        self.dine()

    ## Rosetta's philosopher.dine() implementation
    ##  is fine, so we leave it untouched..
    dine = RosettaPhilosopher.dine

    @property
    def running(self):
        """ translates rosetta's "self.running" semantics to standard cortex semantics """
        return self.started
