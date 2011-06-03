""" cortex.services.terminal.abstract
     stuff that all terminal services have in common.

     this is actually useless until it's bound to the ipython
     console or gui aspect.
"""

from cortex.core import api
from cortex.core.data import EVENT_T
from cortex.services import Service
from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint

class ATerminal(Service, LocalQueue):
    @constraint(boot_first='postoffice')
    def start(self):
        """ """
        from twisted.internet.error import ReactorAlreadyRunning
        # Hack: this raises an exception but everything breaks
        #        without the call itself. hrm..
        self.before_start()
        try:
            self.really_start()
        except ReactorAlreadyRunning:
            pass
        else:
            self.after_start()
        return self

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
        self.postoffice.unsubscribe(EVENT_T, self.push_q)
        report('the Terminal Service Dies.')

    def compute_terminal_namespace(self):
        universe = {'__name__' : '__cortex_shell__',}
        universe.update(api.publish())
        return universe
