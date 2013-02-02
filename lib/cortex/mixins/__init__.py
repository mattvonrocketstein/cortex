""" cortex.mixins

      Collect all the mixins together
"""


import pickle
import time
import StringIO, pprint

from goulash.mixin import Mixin

from cortex.core.util import report, console
from cortex.mixins._os import OSMixin
from cortex.mixins._os import PIDMixin
from cortex.mixins.local_queue import LocalQueue
from cortex.mixins.autonomy import *
from cortex.mixins.persistence import *


class FaultTolerant(Mixin):
    """ faults are a replacement for exceptions """

    def fault(self, error, context={}, **kargs):
        """ TODO: sane yet relatively automatic logging for faults.. """
        if not isinstance(context,dict):
            context = dict(msg=context)
        context.update(kargs)
        context = context or dict(agent=self)
        console.vertical_space()
        console.draw_line()
        print "FAULT:"
        print error
        fhandle = StringIO.StringIO()
        pprint.pprint(context, fhandle)
        print console.color(fhandle.getvalue())
        console.draw_line()
        console.vertical_space()
        self.stop()


class AddressMixin:
    """ Something that's addressable
        TODO: use xanalogica.tumblers
    """


class Controllable(Mixin):

    def halt(self):
        """ like "stop" only safe to call from anywhere """
        ABSTRACT

from spock import Doctrine
from cortex.mixins.mixin import Mixin
class LogicMixin(Mixin, Doctrine): pass

from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
class MobileCodeMixin(object):
    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]
