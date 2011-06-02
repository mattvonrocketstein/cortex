""" cortex.services.terminal

      see also: http://ipython.scipy.org/moin/Cookbook/JobControl

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


from cortex.core import api
from cortex.services import Service
from cortex.core.data import EVENT_T
from cortex.core.util import report, console

from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint

class ShellAspect:
    """ Simple mixin to hold stuff that's pretty IPython specific.
    """
    registry = {}

    def set_prompt(self):
        """ """
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.outputcache.prompt2.p_template = console.red(self.universe.name)  + ' [\\#] '

    def attach_proc(self, func, predicate):
        """ use func when predicate(source)
        """
        if not self.registry:
            first_time = True

        self.registry[func] = predicate
        if first_time:
            self.registry[self.get_input_processor()] = lambda source: "DEFAULT"
            def new_method(source, IP, **kargs): #source, **kargs):
                #raw_input(str(('new',self, args, kargs)))
                #report('new',self, source,kargs)
                for fxn, pred in self.registry.items():
                    test = pred(source)
                    if test and test != "DEFAULT":
                        return fxn(source)
                default_method = [[fxn, pred] for fxn,pred in self.registry.items() if pred('')=="DEFAULT"]
                assert default_method, "No default method found, no attachments fit"
                fxn, pred = default_method.pop()
                return fxn(source)
            self.replace_input_processor(new_method)
        report("attached..")

    def get_input_processor(self):
        """ """
        return self.shell.IP.runsource

    def replace_input_processor(self, new_proc):
        """ replaces the core ipython input processor
            with new_proc, returns the old version
            to caller """
        old = self.get_input_processor() #self.shell.IP.runsource
        self.shell.IP.runsource=new_proc
        return old

    def pre_prompt_hook(self, ip):
        """ IPython-hook to display system notices """
        if self.syndicate_events:
            # extra setup for the postoffice integration..
            #  this stuff is in here because the requires_service() functionality
            #   isn't build yet, so it can't go in start() due to dependancy issues
            if not hasattr(self, 'subscribed'):
                #try:
                (self.universe|'postoffice').subscribe(EVENT_T, self.push_q)
                #except self.universe.services.NotFound:
                #    pass # this service may be ready before the post office
                #         #  is, so this might not work the first time around
                #else:
                self.subscribed = True

            event = self.pop_q()
            if event:
                print console.blue('Events:'), console.color(str(event))


class Terminal(Service, LocalQueue, ShellAspect):
    """ Terminal Service:
          an ipython console that uses the cortex api

            <start>: a few words about starting
            <stop>:  a few words about stopping
    """
    def _post_init(self, syndicate_events_to_terminal=True):
        """
            TODO: self.requires_service('postoffice')
        """
        from cortex.services.terminal.terminal import IPShellTwisted, IPY_ARGS
        self.syndicate_events = syndicate_events_to_terminal
        self.init_q() #initialize for LocalQueue
        universe = {'__name__' : '__cortex_shell__',}
        universe.update(api.publish())
        self.shell = IPShellTwisted(argv=IPY_ARGS, user_ns=universe, controller=self)
        self.set_prompt()
        self.shell.IP.set_hook('pre_prompt_hook', self.pre_prompt_hook)
        self.shell.IP.BANNER = console.draw_line(display=False)

        # install back-ref
        self.universe.terminal = self

    @constraint(boot_first='postoffice')
    def start(self):
        """  TODO: defer to universe.command_line_options for whether to magic_pdb
        """

        # Set IPython "autocall" to "Full"
        self.shell.IP.magic_autocall(2)
        from twisted.internet.error import ReactorAlreadyRunning

        # Hack: this raises an exception but everything breaks
        #        without the call itself. hrm..
        try:
            self.shell.reactor.callWhenRunning(self.shell.on_timer)
            self.shell.start()
            self.shell.reactor.run()
            self.shell.join()
        except ReactorAlreadyRunning:
            pass
        return self


    def stop(self):
        """ overridden from Service.stop to unsubscribe us
            from the postoffice.
        """
        super(Terminal,self).stop()
        self.postoffice.unsubscribe(EVENT_T, self.push_q)
        report('the Terminal Service Dies.')
