""" cortex.demos.philosophers

    Demo of agent-oriented approach for solving dining philosophers.

    Adapted from cortex.demos.philosophers.rosetta

    See also: http://en.wikipedia.org/wiki/Dining_philosophers_problem
"""
""" cortex.demos.philosophers.code

    Rosetta code solution for dining philosphers.

    This is a reference implementation the solution in
    cortex.demos.philsophers.code is adapted from.  Taken
    from: http://rosettacode.org/wiki/Dining_philosophers#Python
"""
import threading
import random
import time

from cortex.mixins.flavors import Threadpooler
from cortex.core.agent import Agent
from cortex.core.util import report

class Philosopher(Agent, Threadpooler):

    def _post_init(self, forkOnLeft=None, forkOnRight=None):
        self.forkOnLeft = forkOnLeft
        self.forkOnRight = forkOnRight

    # self.run() is defined by Threadpooler

    def run_primitive(self):
        time.sleep( random.uniform(1, 3))
        report('%s is hungry.' % self.name)
        self.dine()

    def dine(self):
        fork1, fork2 = self.forkOnLeft, self.forkOnRight

        while self.started:
            fork1.acquire(True)
            locked = fork2.acquire(False)
            if locked: break
            fork1.release()
            report( '%s swaps forks' % self.name )
            fork1, fork2 = fork2, fork1
        else:
            return

        self.dining()
        fork2.release()
        fork1.release()

    def dining(self):
        report( '%s starts eating '% self.name,self.started)
        time.sleep(random.uniform(1,10))
        report( '%s finishes eating and leaves to think.' % self.name)

def DiningPhilosophers():
    forks = [threading.Lock() for n in range(5)]
    philosopherNames = ('Aristotle','Kant','Buddha','Marx', 'Russel')
    philosophers= [ Philosopher(philosopherNames[i], forks[i%5], forks[(i+1)%5]) for i in range(5) ]
    #random.seed(507129)
    #Philosopher.running = True
    #for p in philosophers: p.start()
    #time.sleep(100)
    #Philosopher.running = False
    #print ("Now we're finishing.")

#DiningPhilosophers()
