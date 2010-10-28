""" cortex.core.services.terminal """

from cortex.core import api
from cortex.core.terminal import IPShellTwisted, IPY_ARGS
from cortex.core.util import report
from cortex.core.services import Service

class Terminal(Service):
    """ """
    def play(self):

        universe = {'__name__' : '__cortex_shell__',
                    'universe' : self.universe }
        universe.update(api.publish())
        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe)

        # HACK: this function doesn't return so it wont be added automatically like
        #       the other services are
        self.universe._services += [self]

        self.shell.mainloop()
        report('the Terminal Service Dies.')
