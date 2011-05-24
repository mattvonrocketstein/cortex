""" tests for cortex

    turns out the best place to run tests are
    to be inside the system that's being tested..
"""

from cortex.core import api
from cortex.demos.philosophers import Philosopher

#.code import Philosopher

## Parameters for the services.. empty and ready to override
#interactive = True                                   # Whether to run shell
interactive = True                                  # Whether to run shell
post_args   = {}                                     # Postoffice parameters
term_args   = {}                                     # Cortex-Terminal arguments
linda_args  = {}                                     # Linda (tuplespace) parameters

## Build a list of instructions recognizable to the cortex api.  Order does not matter
## here because the service definitions specify (and resolve) their own dependencies.
instructions         = [[ "load_service", ("_linda",),          linda_args ],
                        [ "load_service", ("postoffice",),      post_args  ],]
terminal_instruction = [[ "load_service", ("terminal",),        term_args  ],]
if interactive: instructions += terminal_instruction


# Specify terminating conditions to declare as goals
philosophers_finished = lambda: False



def DiningPhilosophers():
    import threading
    forks = [threading.Lock() for n in range(5)]
    philosopherNames = ('Aristotle','Kant','Buddha','Marx', 'Russel')
    philosophers= [ api.universe.agents(Philosopher,name=philosopherNames[i],
                                    **dict(forkOnLeft=forks[i%5], forkOnRight=forks[(i+1)%5]))
                    for i in range(5)]

DiningPhilosophers()



# Declare goals, load services with the given parameters, and invoke mainloop
api.declare_goals( [ philosophers_finished ] )
api.do( instructions )
api.universe.play()
