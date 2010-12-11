""" cortex.contrib.promela.hlpers
"""

from cortex.core.util import report

def tasks_from_predicates(predicates, on_failure):
    """ used for the <never> guard's functionality """
    tasks = []

    for predicate in predicates:
        task = lambda: ( (not predicate()) and on_failure() )
        tasks.append(task)
    return tasks
