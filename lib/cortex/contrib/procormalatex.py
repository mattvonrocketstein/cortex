""" cortex.contrib.procormaltex:
    promela** concepts in cortex

    **: the "process or protocol meta language"
        see http://spinroot.com/spin/Man/Quick.html


Special variables
    + _pid, _last

    _pid is a predefined local variable that holds the
    instantiation number of the process' instance. _last
    is a predefined global variable that holds the instantiation
    number of the process instance that performed the last step
    in the current execution sequence. Initially, _last is zero.


Remote references
  The expression:

    + procname[pid]@label

  is true precisely if the process with
  instantiation number pid of proctype
  procname is currently at the statement
  labeled with label.


"""
from cortex.core.agent import Agent

class PromelaCore(object):
    def never(statements):
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

            Never claims can use three additional functions:

                * enabled(pid) This boolean function returns
                  true if the process with instantiation number
                  denoted by pid is able to perform an operation.
                  This function can only be used in systems that
                  do not admit synchronous communication

                * pc_value(pid) This function returns the number
                  of the state that the process with instantiation
                  number denoted by pid is currently in. ( With
                  state-numbers as given by the -d runtime option. )

                * _np This predicate is true if the system is in a
                  non-progress state and is false otherwise. It is
                  introduced to enable more efficient searches for
                  non-progress cycles. See progress and SearchNPC.
        """
    def init(proc):
    """ Init process
          init { statements }

          This process, if present, is instantiated once, and
          is often used to prepare the true initial state of a
          system by initializing variables and running the
          appropriate process-instances.
    """
    pass

class Process(Agent):
    """ Processes
        A basic process declaration has the form

            proctype pname( chan In, Out; byte id )
            { statements }
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

    def run(self):
        """ Such a process is instantiated by a run-operation:

               run pname(Transfer, Device[0], 0)

            that first assigns the actual parameters to the formal
            ones and then executes the statements in the body. Each
            process instance has a unique, positive instantiation
            number, which is yielded by the run-operator (and by pid);
            see specvar. A process-instance remains active until the
            process' body terminates (if ever).
        """

        """
           Processes cannot have arrays as (part of) a formal parameter type,
           but structures are allowed.

           Process declarations can be augmented in various ways.
           The most general form is

               active [N] proctype pname(...) provided (E) priority M

           The active modifier causes N instances of the proctype to be
           active in the initial system state, where N is a constant. If
           [N] is absent, only one instance is activated. Formal parameters
           of instances activated through the active modifier are initialized
           to 0; i.e. actual parameters can only be passed using run-statements.

           A proctype can have an enabling condition E associated with it,
           which is a general side-effect free expression that may contain
           constants, global variables, the predefined variables timeout and
           pid, but not other local variables or parameters, and no remote
           references. Enabling conditions are evaluated once, in the initial
           state.

           For use during random simulations, a process instance can run with
           a priority M, a constant >=1. Such a process is M times as likely
           to be scheduled than a default (priority 1) process. Execution
           priorities can be used in a run-statement as well:

               run pname(...) priority M

           A process instantiated with a run statement always gets the priority
           that is explicitly or implicitly specified there (the default is 1).

           Note that priorities have no effect during analysis.
    """
