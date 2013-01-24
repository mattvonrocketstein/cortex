""" cortex.demos.philosophers:
      Demo of agent-oriented approach for solving dining philosophers.

    See also:
      cortex.demos.philosophers.rosetta: reference implementation
      http://en.wikipedia.org/wiki/Dining_philosophers_problem

"""

from twisted.internet.defer import Deferred

from cortex.core.agent import Agent
from cortex.mixins import Mixin
from cortex.core.util import alias
from cortex.mixins.flavors import ThreadedAgent, ReactorRecursion

from cortex.demos.philosophers.rosetta import Philosopher as PhilosopherTemplate

class PhilosopherOverrides(Mixin):
    """ This class is a thin wrapper around the rosetta example

        It serves as a demo for how to "agentify" any random threaded code.

        NOTE: PhilosopherTemplate.run() is not used! run() is inherited from ThreadedAgent
    """
    def _post_init(self, forkOnLeft=None, forkOnRight=None):
        """ replacement: PhilosopherTemplate.__init__ """
        self.forkOnLeft = forkOnLeft
        self.forkOnRight = forkOnRight

    def run_primitive(self):
        """ replacement: PhilosopherTemplate.run()

            the loop there is essentially already
            abstracted upwards into ThreadedAgent.run()
        """
        d = Deferred()
        def yam():
            self.wait() # without arguments, blocks for one second
            print('%s is hungry.' % self.name)
            self.dine()
        self.universe.reactor.callLater(.1, yam)

    ## Rosetta's philosopher.dine() implementation is fine
    dine = PhilosopherTemplate.dine

    # PhilosopherTemplate.running is equivalent to cortex's Agent.started
    running = alias('started')


ReactivePhilosopher = Agent.using(template=PhilosopherTemplate,
                                  flavor=ReactorRecursion)
ThreadedPhilosopher = Agent.using(template=PhilosopherTemplate,
                                  flavor=ThreadedAgent)

#class Philosopher(PhilosopherOverrides, ReactivePhilosopher): iteration_period = 1
class Philosopher(PhilosopherOverrides, ThreadedPhilosopher): pass
