""" cortex.contrib.promela.process
"""

from cortex.core.util import report
from cortex.core.agent import Agent

class Process(Agent):
    """ Processes
        A basic process declaration has the form

            proctype pname( chan In, Out; byte id )
            { statements }

        Special variables
            + _pid, _last

              _pid is a predefined local variable that holds
              the instantiation number of the process'
              instance. _last is a predefined global variable
              that holds the instantiation number of the process
              instance that performed the last step in the current
              execution sequence. Initially, _last is zero.
    """
    def post_init(self, _in=None, _out=None, _id=None,
                  deterministic=False, **kargs):
        """
        Deterministic processes

            D_proctype pname( chan In, Out; byte id ){ statements }

            declares that any instance of pname is deterministic.
            It has no other effect, then causing an error during
            analysis if some instance is not.

            Note that determinism is a dynamic property. E.g., if
            pname has in its body the statement

            if
            :: In?v  -> ...
            :: Out!e -> ...
            fi

            then non-determinism is flagged only if during some computation,
            there is an instance of pname for which the receive and send on
            the actual channels bound to In and Out are simultaneously enabled.
    """
