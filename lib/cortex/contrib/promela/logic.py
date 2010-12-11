""" cortex.contrib.promela.logic
"""

class Predicates:
    """  Never claims can use three additional functions:

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
