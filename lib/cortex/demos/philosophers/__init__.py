""" cortex.demos.philosophers:
      Demo of agent-oriented approach for solving dining philosophers.

    See also:
      cortex.demos.philosophers.rosetta: reference implementation
      http://en.wikipedia.org/wiki/Dining_philosophers_problem

"""

from cortex.mixins.flavors import ThreadedAgent
from cortex.demos.philosophers.rosetta import Philosopher as PhilosopherTemplate
from cortex.core.agent import Agent


class PhilosopherOverrides(object):
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
        self.wait() # without arguments, blocks for one second
        print('%s is hungry.' % self.name)
        self.dine()

    ## Rosetta's philosopher.dine() implementation is fine
    dine = PhilosopherTemplate.dine

    @property
    def running(self):
        """ translation: PhilosopherTemplate.running is
            semantically equivalent cortex's Agent.started """
        return self.started


PhilosopherTemplate = Agent.template_from(PhilosopherTemplate)
ThreadedPhilosopher = PhilosopherTemplate.use_concurrency_scheme(ThreadedAgent)



#class PhilosopherTemplate(Agent,PhilosopherTemplate):
#    pass #= Agent.subclass('PhilosopherTemplate',**dict(PhilosopherTemplate.__dict__))
#class Philosopher(PhilosopherOverrides, ConcurrencyStle, PhilosopherTemplate):
#    pass

class Philosopher(PhilosopherOverrides, ThreadedPhilosopher):#.bind_to(ConcurrencyStle)):
    pass
