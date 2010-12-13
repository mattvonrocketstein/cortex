""" cortex.contrib.promela.commands
"""
def atomic(statements):
        """ The Atomic Construct atomic {statements;}

              By prefixing a sequence of statements enclosed in curly braces
              with the keyword atomic the user can indicate that the sequence
              is to be executed as one indivisible unit, non-interleaved with
              any other processes.

              It is a runtime error if any statement, other than the first
              statement, blocks in an atomic sequence. Atomic sequences can
              be an important tool in reducing the complexity of verification
              models. Note that atomic sequences restricts the amount of
              interleaving that is allowed in a distributed system. Intractable
              models can be made tractable by labeling all manipulations of
              local variables with atomic sequences.
        """
        return statements

def run(self):
    """ Such a process is instantiated by a run-operation:

          + run pname(Transfer, Device[0], 0)

        that first assigns the actual parameters to the formal
        ones and then executes the statements in the body. Each
        process instance has a unique, positive instantiation
        number, which is yielded by the run-operator (and by pid);
        see specvar. A process-instance remains active until the
        process' body terminates (if ever).
    """
    pass

def active(self):
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

def init(proc):
        """ Init process
              init { statements }

              This process, if present, is instantiated once, and
              is often used to prepare the true initial state of a
              system by initializing variables and running the
              appropriate process-instances.
        """
        pass
