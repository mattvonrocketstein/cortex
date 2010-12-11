""" example boot script for cortex, demonstrates the task iterator
"""

from cortex.core import api
from cortex.agents import TaskIterator
from cortex.core.api import InstructionSet
from cortex.contrib.procormalatex import PromelaCore

# some dumb task examples
def task1(): print 'zam1'
def task2(): print 'zam2'
def task3(): print 'zam3'

InstructionSet = InstructionSet()
InstructionSet.load_service('_linda'),
InstructionSet.load_service('postoffice'),
InstructionSet.load_service('terminal'),
InstructionSet.build_agent('task-agent',
                           kls      = TaskIterator,
                           universe = api.universe,
                           tasks    = [task1, task2, task3] )
InstructionSet.append(PromelaCore.never( [ lambda: False ] ))
InstructionSet.finish()

# Invoke the universe (mainloop)
api.universe.play()
