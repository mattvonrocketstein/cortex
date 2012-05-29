""" cortex.services.terminal.abstract

     stuff that all terminal services have in common.
     this is useless until it's bound to the concrete
     ipython console or gui aspect.
"""

from cortex.core import api
from cortex.services import Service
from cortex.mixins import LocalQueue
from cortex.core.data import EVENT_T
from cortex.core.util import report, console
from cortex.util.decorators import constraint
from cortex.services.api import CHAN_NAME

class ATerminal(Service, LocalQueue):
    """ """
    class Meta:
        subscriptions = {CHAN_NAME: 'contribute_to_api'}

    @constraint(boot_first='postoffice')
    def start(self):
        """ """
        super(ATerminal, self).start()
        from twisted.internet.error import ReactorAlreadyRunning
        # Hack: this raises an exception but everything breaks
        #        without the call itself. hrm.
        self.before_start()
        try:
            self.really_start()
        except ReactorAlreadyRunning:
            pass
        else:
            self.after_start()

    def before_start(self):
        report('abstract before_start')

    def after_start(self):
        pass

    def set_prompt(self):
        """ """
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.outputcache.prompt2.p_template = console.red(self.universe.name)  + ' [\\#] '

    def _post_init(self, syndicate_events_to_terminal=True):
        """ install back-reference in universe,
            initialize the local queue
        """
        self.syndicate_events  = syndicate_events_to_terminal
        self.universe.terminal = self

        # initialize for LocalQueue
        self.init_q()

    def stop(self):
        """ overridden from Service.stop to unsubscribe us
            from the postoffice.
        """
        super(ATerminal,self).stop()
        if self.universe.started:
            (self.universe|'postoffice').unsubscribe(EVENT_T, self.push_q)
        try:
            self.shell.IP.ipmagic('exit')
        except:
            report('failure with ipmagic exit.  (is this the gui?)')
        report('the Terminal Service Dies.')

    def contribute_to_api(self, **namespace):
        came_from = namespace.pop('__channel', None)
        self.shell.IP.user_ns.update(**namespace)

    @staticmethod
    def compute_terminal_namespace():
        """ populates the namespace that is available within the shell """
        import inspect
        namespace = {'__name__' : '__cortex_shell__',}
        namespace.update(api.publish())
        namespace.update(dict(getfile=inspect.getfile))
        return namespace
