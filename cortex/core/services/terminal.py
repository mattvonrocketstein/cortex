""" cortex.core.services.terminal """

from cortex.core import api
from cortex.core.util import report
from cortex.core.services import Service
from cortex.core.terminal import IPShellTwisted, IPY_ARGS

class Terminal(Service):
    """ Terminal Service:
          start:
          stop:
    """

    def begin(self):
        """ """
        self.shell.mainloop()
        report('the Terminal Service Dies.')

    def play(self):
        """ """
        universe = {'__name__' : '__cortex_shell__',
                    'universe' : self.universe,
                    'services' : self.universe.services,}
        universe.update(api.publish())
        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe)

        return self
