""" cortex.core.services.terminal """

from cortex.core import api
from cortex.core.util import report
from cortex.core.services import Service
from cortex.core.terminal import IPShellTwisted, IPY_ARGS

class Terminal(Service):
    """ Terminal Service:
         an ipython console that uses the cortex api

          start:
          stop:
    """

    def _post_init(self):
        universe = {'__name__' : '__cortex_shell__',
                    'universe' : self.universe,
                    'services' : self.universe.services,}
        universe.update(api.publish())
        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe)

    def start(self):
        """ """
        self.shell.mainloop()
        report('the Terminal Service Dies.')

    def stop(self):
        """ """
        report('NIY')

    def play(self):
        """ """
        #self.universe.reactor.callLater(1, self.start)
        self.start()
        return self
