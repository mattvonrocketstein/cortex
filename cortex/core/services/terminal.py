""" cortex.core.services.terminal
      see also: http://ipython.scipy.org/moin/Cookbook/JobControl
"""

from cortex.core import api
from cortex.core.util import report, console#, notifier
from cortex.core.services import Service
from cortex.core.terminal import IPShellTwisted, IPY_ARGS

class Terminal(Service):
    """ Terminal Service:
         an ipython console that uses the cortex api

           start:
           stop:
    """

    def _post_init(self):
        """ """
        universe = {'__name__' : '__cortex_shell__',
                    'services' : list(self.universe.services),
                   }
        universe.update(api.publish())


        def pre_prompt_hook(ip):
            """ IPython hook to display system notices
            """
            print console.blue('Events:'),console.color(str(self.universe.notices))


        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe,controller=self)
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.set_hook('pre_prompt_hook',pre_prompt_hook)
        self.universe.terminal = self

    def start(self):
        """ """
        # Set IPython "autocall" to "Full"
        self.shell.IP.magic_autocall(2)
        from twisted.internet.error import ReactorAlreadyRunning

        # Hack: this raises an exception but everything breaks
        #        without the call itself. hrm..
        try:
            self.shell.mainloop()
        except ReactorAlreadyRunning:
            pass

        return self


    def stop(self):
        """ """
        super(Terminal,self).stop()
        report('the Terminal Service Dies.')

    def play(self):
        """ """
        self.universe.reactor.callLater(1, self.start)
        return self
