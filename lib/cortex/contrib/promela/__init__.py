""" cortex.contrib.promela: promela in cortex

    An implementation of various Promela concepts in Cortex.

        Promela is the "process or protocol meta language", and
        procedures implemented in it have various properties that
        can be exploited for model-verification with the "spin"
        tool.

    see also: specification at http://spinroot.com/spin/Man/Quick.html

methods inside PromelaCore should generate cortex
compatible instructionsets for doing an equivalent
operation.

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
#from cortex.core.agent import Agent
from cortex.core.api import InstructionSet
from cortex.contrib.promela.claims import never
from cortex.contrib.promela.logic import Predicates
from cortex.contrib.promela._process import Process
