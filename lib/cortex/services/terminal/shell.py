""" cortex.services.terminal.shell
"""

from cortex.core.util import report, console

class ShellAspect:
    """ Simple mixin to hold stuff that's pretty IPython specific.
    """
    registry = {}

    def before_start(self):
        self.set_shell()
        self.set_prompt()

    def set_shell(self):
        from cortex.services.terminal.terminal import IPShellTwisted, IPY_ARGS
        self.shell = IPShellTwisted(argv=IPY_ARGS,
                                    user_ns=self.compute_terminal_namespace(),
                                    controller=self)
        self.shell.IP.set_hook('pre_prompt_hook', self.pre_prompt_hook)
        self.shell.IP.BANNER = console.draw_line(display=False)

    def really_start(self):
        """ TODO: defer to universe.command_line_options for whether to magic_pdb """
        # This case is nasty..  nothing seems to be able to make the process exit cleanly
        if self.universe.command_line_options.gtk_reactor==True:
            err = ("This universe is configured for the GTK reactor, "
                   "but you're trying to use the console-based ipython terminal.")
            ctx = 'test'
            self.fault(err, ctx)
            self.universe.halt()
            #import sys;sys.exit()

        self.shell.reactor.callWhenRunning(self.shell.on_timer)
        self.shell.start()
        self.shell.reactor.run()
        self.shell.join()

    def attach_proc(self, func, predicate):
        """ use func when predicate(source)
        """
        if not self.registry:
            first_time = True

        self.registry[func] = predicate
        if first_time:
            self.registry[self.get_input_processor()] = lambda source: "DEFAULT"
            def new_method(source, IP, **kargs): #source, **kargs):
                for fxn, pred in self.registry.items():
                    test = pred(source)
                    if test and test != "DEFAULT":
                        return fxn(source)
                default_method = [ [fxn, pred] for fxn,pred in self.registry.items() \
                                   if pred('')=="DEFAULT" ]
                assert default_method, "No default method found, no attachments fit"
                fxn, pred = default_method.pop()
                return fxn(source)
            self.replace_input_processor(new_method)
        report("attached..")

    def get_input_processor(self): return self.shell.IP.runsource

    def replace_input_processor(self, new_proc):
        """ replaces the core ipython input processor
            with new_proc, returns the old version
            to caller """
        old = self.get_input_processor() #self.shell.IP.runsource
        self.shell.IP.runsource = new_proc
        return old

    def pre_prompt_hook(self, ip):
        """ IPython-hook to display system notices """
        if self.syndicate_events:
            event = self.pop_q()
            if event:
                print console.blue('Events:'), console.color(str(event))
