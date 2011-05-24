""" tests for cortex

    turns out the best place to run tests are
    to be inside the system that's being tested..
"""
from cortex.core.api import universe, declare_agent, load_instructions
from cortex.demos.philosophers import Philosopher
from cortex.instructions import LOAD_LINDA, LOAD_POST_OFFICE
from cortex.core.util import Lock

## Build a list of instructions recognizable to the cortex api.  Order does not matter
## here because the service definitions specify (and resolve) their own dependencies.
instructions         = [ LOAD_LINDA, LOAD_POST_OFFICE, LOAD_TERMINAL]

## Adapted from initialization sequence described in:
##  cortex.demos.philosophers.rosetta.DiningPhilosophers
forks = [Lock() for n in range(5)]
philosopherNames = ('Aristotle','Kant','Buddha','Marx', 'Russel')
for i in range(5):
    fork1 = forks[i%5]
    fork2 = forks[(i+1)%5]
    declare_agent(Philosopher,
                  name=philosopherNames[i],
                  forkOnLeft=fork1,
                  forkOnRight=fork2)

# Load services with the given parameters, and invoke mainloop
load_instructions( instructions )
universe.play()
