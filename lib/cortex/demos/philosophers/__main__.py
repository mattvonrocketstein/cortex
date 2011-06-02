""" cortex.demos.philosophers.__main__

    Demonstrates how to use threaded code with cortex, using a very minimal wrapper on top
    of rosetta code's dining-philosophers implementation.  Now that these philosophers are
    proper agents, they (or the developer) can leverage any of the bells and whistles that
    are available in the form of cortex services.  The only "extra" that is actually used
    here is the terminal service, which allows the developer to inspect the agents, or any
    other part of the universe, while it is running.

    Here are a few obvious ways to improve this example using features offered by cortex:

      0) Pave the way for a solution using an arbiter-pattern: build a custom AgentManager.
         All philosophers would be registered with it, and it would be registered with the
         universe.  This minimal example just uses the universe itself to hold the philosophers;
         the universe, among other things, functions as an agentmanager.

      1) Change all the "print" statements to use the event channel.

      2) Generate the implementation of RosettaPhilosopher.dine() from a description of agent
         behaviour.

      3) Build a watchdog that verifies that no philosopher is starving

      4) Declare goals so that the universe terminates after every philosopher has eaten at
         least N times.

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
    forks = [ Lock() for n in range(5) ]
    for fork in forks:
        fork.fork_num = forks.index(fork)


    philosopherNames = ('Aristotle','Kant','Buddha','Marx', 'Russel')
    for i in range(5):
        args  = dict( forkOnLeft = forks[i%5],
                      forkOnRight = forks[(i+1)%5],
                      name = philosopherNames[i] )
        declare_agent(Philosopher, **args)

## Setup agents and load them into the universe.
## A better way would be to use an agent-manager rather than  using the
## universe itself directly, which paves the way to solving the problem
## with an arbiter, but this is the most minimal example possible.
initialize()

# Load services with the default (parameterless) instructions
load_instructions( instructions )

# Invoke the mainloop
universe.play()
