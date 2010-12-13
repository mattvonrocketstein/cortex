""" cortex.contrib.promela: promela in cortex

    An implementation of various Promela concepts in Cortex.

        Promela is the "process or protocol meta language", and
        procedures implemented in it have various properties that
        can be exploited for model-verification with the "spin"
        tool.

        See also:
            promela specification:           http://spinroot.com/spin/Man/Quick.html
            overview of spin model checker:  http://spinroot.com/spin/whatispin.html#A

    The goal is to gernate cortex compatible instructionsets for doing
    semantically equivalent promela operations.

"""

class Notation(object):
    """ Remote references
        The expression:

          + procname[pid]@label

        is true precisely if the process with
        instantiation number pid of proctype
        procname is currently at the statement
        labeled with label.
    """

from cortex.core.util import report
from cortex.core.api import InstructionSet
from cortex.contrib.promela.claims import never
from cortex.contrib.promela.logic import Predicates
from cortex.contrib.promela._process import Process
