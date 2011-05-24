""" cortex.demos.philosophers.__main__

    Demonstrates how to use threaded code with cortex, using a very minimal wrapper
    on top of rosetta code's dining philosophers implementation.  Now that these
    philosophers are proper agents, they (or the developer) can leverage any of the
    bells and whistles that are available in the form of cortex services.  The only
    one that is actually used is the terminal service, which allows the developer
    to inspect the agents, or any other part of the universe, as it is running.

"""
from cortex.demos.philosophers import Philosopher
from cortex.core.api import universe, declare_agent, load_instructions
from cortex.instructions import LOAD_LINDA, LOAD_POST_OFFICE, LOAD_TERMINAL
from cortex.core.util import Lock

## Build a list of instructions recognizable to the cortex api.  Order does not matter
## here because the service definitions specify (and resolve) their own dependencies.
instructions         = [ LOAD_LINDA, LOAD_POST_OFFICE, LOAD_TERMINAL]

def initialize():
    """ Adapted from initialization sequence described in:
          cortex.demos.philosophers.rosetta.DiningPhilosophers
    """
    forks = [Lock() for n in range(5)]
    philosopherNames = ('Aristotle','Kant','Buddha','Marx', 'Russel')
    for i in range(5):
        fork1 = forks[i%5]
        fork2 = forks[(i+1)%5]
        declare_agent(Philosopher,
                      name=philosopherNames[i],
                      forkOnLeft=fork1,
                      forkOnRight=fork2)

# Setup agents and load them into the universe.
# A better way is to use an agent-manager rather than
# using the universe itself directly, which paves the
# way to solving the problem with an arbiter, but this
# is the most minimal example.
initialize()

# Load services with the default (parameterless)
# instructions and then invoke the mainloop
load_instructions( instructions )
universe.play()
