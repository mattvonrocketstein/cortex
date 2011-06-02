""" cortex.services.terminal.terminal

      Adapted from: http://code.activestate.com/recipes/410670-integrating-twisted-reactor-with-ipython/

      TODO: this appears to be in twshell in ipython 0.10.1 .. extend that
"""
import threading

from IPython.Shell import MTInteractiveShell
from IPython.ipmaker import make_IPython

from cortex.core.data import IPY_ARGS

def hijack_reactor():
    """Modifies Twisted's reactor with a dummy so user code does
    not block IPython.  This function returns the original
    'twisted.internet.reactor' that has been hijacked.

    NOTE: Make sure you call this *AFTER* you've installed
    the reactor of your choice.
    """
    from twisted import internet
    orig_reactor = internet.reactor

    class DummyReactor(object):
        def run(self):
            pass
        def __getattr__(self, name):
            return getattr(orig_reactor, name)
        def __setattr__(self, name, value):
            return setattr(orig_reactor, name, value)

    internet.reactor = DummyReactor()
    return orig_reactor


class IPShellTwisted(threading.Thread):
    """Run a Twisted reactor while in an IPython session.

    Python commands can be passed to the thread where they will be
    executed.  This is implemented by periodically checking for
    passed code using a Twisted reactor callback.
    """

    TIMEOUT = 0.03 # Millisecond interval between reactor runs.

    def __init__(self, argv=None, user_ns=None, controller=None,debug=1,
                 shell_class=MTInteractiveShell):
        self.controller=controller
        from twisted.internet import reactor
        self.reactor = hijack_reactor()

        self.mainquit = self.reactor.stop

        # Make sure IPython keeps going after reactor stop.
        def reactorstop():
            pass

        self.reactor.stop = reactorstop
        reactorrun_orig = self.reactor.run
        self.quitting = False
        def reactorrun():
            while True and not self.quitting:
                reactorrun_orig()
        self.reactor.run = reactorrun

        self.IP = make_IPython(argv, user_ns=user_ns, debug=debug,
                               shell_class=shell_class,
                               on_kill=[self.mainquit,self.controller.universe.sleep])
        threading.Thread.__init__(self)

    def run(self):
        self.IP.mainloop()
        self.quitting = True
        self.IP.kill()

    def on_timer(self):
        self.IP.runcode()
        self.reactor.callLater(self.TIMEOUT, self.on_timer)
