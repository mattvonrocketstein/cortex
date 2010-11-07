""" cortex.services.beacon

import sys
from IPython.Debugger import Pdb
from IPython.Shell import IPShell
from IPython import ipapi

shell = IPShell(argv=[''])

def set_trace():
    ip = ipapi.get()
    def_colors = ip.options.colors
    Pdb(def_colors).set_trace(sys._getframe().f_back)


"""

from cortex.core.util import report
from cortex.core.services import Service

class Beacon(Service):
    """ Beacon Service:
          start:
          stop:
    """

    def _post_init(self):
        self.is_stopped = False

    def stop(self):
        """ """
        self.is_stopped = True

    def beacon(self):
        if not self.is_stopped:
            self.universe.reactor.callLater(1, self.beacon)
        print " blip "

    def play(self):
        self.universe.reactor.callLater(1,self.beacon)
        return self
