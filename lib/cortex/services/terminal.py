""" cortex.services.terminal
      see also: http://ipython.scipy.org/moin/Cookbook/JobControl
"""


from cortex.core import api
from cortex.services import Service
from cortex.core.data import EVENT_T
from cortex.core.util import report, console
from cortex.core.terminal import IPShellTwisted, IPY_ARGS
from cortex.core.mixins import LocalQueue

class Terminal(Service, LocalQueue):
    """ Terminal Service:
          an ipython console that uses the cortex api

            <start>: a few words about starting
            <stop>:  a few words about stopping
    """

    def _post_init(self):
        """
            TODO: self.requires_service('postoffice')
        """
        self.init_q() #initialize for LocalQueue
        universe = {'__name__' : '__cortex_shell__',}
        universe.update(api.publish())

        def pre_prompt_hook(ip):
            """ IPython-hook to display system notices """

            # extra setup for the postoffice integration..
            #  this stuff is in here because the requires_service() functionality
            #   isn't build yet, so it can't go in start() due to dependancy issues
            if not hasattr(self,'subscribed'):
                try:
                    (self.universe|'postoffice').subscribe(EVENT_T, self.push_q)
                except self.universe.services.NotFound:
                    pass # this service may be ready before the post office
                         #  is, so this might not work the first time around
                else:
                    self.subscribed = True

            event = self.pop_q()
            if event:
                print console.blue('Events:'), console.color(str(event))

        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe, controller=self)
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.outputcache.prompt2.p_template = console.red(self.universe.name) + ' [\\#] '
        self.shell.IP.set_hook('pre_prompt_hook', pre_prompt_hook)
        #self.shell.IP.BANNER = "Eat a sandwich.  see if i care."
        self.universe.terminal = self

    def start(self):
        """  TODO: defer to universe.command_line_options for whether to magic_pdb
        """
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
        self.postoffice.unsubscribe(EVENT_T, self.push_q)
        report('the Terminal Service Dies.')

    def play(self):
        """ """
        self.universe.reactor.callLater(1, self.start)

        return self
