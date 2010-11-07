""" cortex.core.services.terminal """

from cortex.core import api
from cortex.core.util import report
from cortex.core.services import Service
from cortex.core.terminal import IPShellTwisted, IPY_ARGS
# see also: http://ipython.scipy.org/moin/Cookbook/JobControl
class Terminal(Service):
    """ Terminal Service:
         an ipython console that uses the cortex api

          start:
          stop:
    """

    def _post_init(self):
        """ """
        universe = {'__name__' : '__cortex_shell__',
                    'sleep'    :   self.universe.sleep,
                    #Now published by api
                    #'universe' : self.universe,
                    #'load_service' : self.universe.loadService,
                    'services' : list(self.universe.services),}
        universe.update(api.publish())


        def pre_prompt_hook(ip):
            print 'Events', self.universe.events

        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe,controller=self)
        self.shell.IP.set_hook('pre_prompt_hook',pre_prompt_hook)
        self.universe.terminal = self

    def start(self):
        """ """
        # Set IPython "autocall" to "Full"
        self.shell.IP.magic_autocall(2)
        from twisted.internet.error import ReactorAlreadyRunning
        try:
            self.shell.mainloop()
        except ReactorAlreadyRunning:
            pass
        return self

    def stop(self):
        """ """
        report('the Terminal Service Dies.')

    def play(self):
        """ """
        self.universe.reactor.callLater(1, self.start)
        #self.start()
        return self
