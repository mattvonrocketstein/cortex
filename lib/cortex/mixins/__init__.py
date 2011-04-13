""" cortex.mixins.__init__

      Collect all the mixins together
"""


import pickle
import time

from cortex.core.util import report, console
from cortex.mixins._os import OSMixin
from cortex.mixins._os import PIDMixin
from cortex.mixins.local_queue import LocalQueue
from cortex.mixins.mobility import MobileCodeMixin
from cortex.mixins.autonomy import *
from cortex.mixins.mixin import Mixin

class FaultTolerant(Mixin):
    """ faults are a replacement for exceptions """
    def fault(self, error, context):
        """ TODO: sane yet relatively automatic logging for faults.. """
        console.vertical_space()
        report("",header=console.red("--> FAULT <--"))
        console.draw_line()
        print ( "\n{error}".format(error=error))
        import StringIO, pprint
        fhandle = StringIO.StringIO()
        pprint.pprint(context, fhandle)
        print console.color(fhandle.getvalue())
        console.draw_line()
        console.vertical_space()

class AddressMixin:
    """ Something that's addressable """

from cortex.mixins.persistence import *



class ControllableMixin(Mixin):
    def halt(self):
        """ like "stop" only safe to call from anywhere """
        ABSTRACT



class PerspectiveMixin:
    """
    def ground(self):
        ''' placeholder: run filters on the ground here, ie
              + grab only some particular named subspace, or
              + pre-processing, post-processing, misc. mutation
        '''
        return self.universe.ground
    """

    def darkly(self):
        """ if this agent refers to a local version, ie is a nonproxy, obtain
            an image of self suitable for acurate transmission/storage/reinvocation
            elsewhere
        """
        image = self.serialize()
        return NY

    # Aliases
    shadow = shadowed = darkly
