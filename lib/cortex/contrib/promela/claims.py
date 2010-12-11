""" cortex.contrib.promela.claims
"""

from cortex.core.api import InstructionSet

def never(predicates):
    """ Never claim

             + never { statements }

           is a special type of process that, if present, is
           instantiated once. As explained further in tempclaim,
           never claims are used to detect behaviors that are
           considered undesirable or illegal.

           The individual statements in statements are interpreted
           as conditions (see Exec and ExprStat) and, therefore,
           should not have side-effects (although this will cause
           warnings rather than syntax-errors).

           Statements that can have side-effect are assignments,
           auto-increment and decrement operations, communications,
           run and assert statements.
    """
    from cortex.agents.workers import TaskIterator
    from cortex.core import api
    def tasks_from_predicates(predicates):
            tasks = []
            for predicate in predicates:
                msg  = "Predicate entered into <never> was False!"
                task = lambda: ( (not predicate()) and \
                                 report(msg) )
                tasks.append(task)
            return tasks
    instructions = InstructionSet()
    tasks = tasks_from_predicates(predicates)
    name  = 'never:{N}:{id}'.format(N=len(predicates),
                                    id=str(id(predicates)))
    return instructions.build_agent( name     = name,
                                     kls      = TaskIterator,
                                     universe = api.universe,
                                     tasks    = tasks )
