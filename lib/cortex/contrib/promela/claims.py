""" cortex.contrib.promela.claims

       Never claim:

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


from cortex.core import api
from cortex.core.util import report
from cortex.contrib.promela import helpers
from cortex.agents.workers import TaskIterator
from cortex.core.instructions import InstructionSet

failure_msg  = "Predicate entered into <never> was False!"
on_failure_report=lambda:report(failure_msg)

def never(predicates, name=None, on_failure=None):
    """ returns instructions that implement the never claim in cortex.

        on_failure::
          a method that will be run in case of failure to verify claim
          the default is to use <report> to log it.

        name ::
          a name for the agent that will effect this claim.
          a default will be generated if it is not given
    """

    # Derive on_failure if not given
    if on_failure is None:
        on_failure = on_failure_report

    # Build tasks and set name if not given
    tasks = helpers.tasks_from_predicates(predicates, on_failure=on_failure)
    name  = name or 'never:{N}:{id}'.format(N=len(predicates), id=str(id(predicates)))

    # Grab an instructionset to write to, and build instruction
    instructions = InstructionSet()
    instruction  = instructions.build_agent( name     = name,
                                             kls      = TaskIterator,
                                             universe = api.universe,
                                             tasks    = tasks )
    return instruction
