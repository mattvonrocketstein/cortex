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
