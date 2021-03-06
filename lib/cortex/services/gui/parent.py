""" cortex.services.gui.parent
"""
from ipython_view import *
from common import CommonInterface
from cortex.services.terminal import abstract
from cortex.core.util import report

class GUI(CommonInterface):
    """ """

    def set_shell(self):
        """ get a gtk-embedded ipython thingy
            this function might seem like it has a
            weird name, but it's named to be similar
            to the one in cortex.services.terminal.shell
        """
        S = self.scrolled_window
        from cortex.core.data import IPY_ARGS
        self.shell = IPythonView(argv=IPY_ARGS,
                        user_ns=abstract.ATerminal .compute_terminal_namespace())

        self.shell.show()
        S.add(self.shell)
        S.show()
        return S

    def sanity(self):
        if not self.universe.command_line_options.gtk_reactor==True:
            err  = "This universe isn't configured for GTK reactor, "
            err += "but you're trying to use the gtk terminal!"
            ctx  = str(self)
            self.fault(err, ctx)
            self.universe.stop()

    def really_start(self):
        self.sanity()

        # pretty much the minimal requirements for agent's __init__
        # in this case it's sort of implied, so how best to remove
        # that boiler plate?
        ctx = dict(universe=self.universe)

        # Build an agent/window suitable for monitoring
        # the event channel (which handles peer-discovery)
        from cortex.services.gui.channel_window import channel_agent_factory
        from channel import ChannelType


        # NOTE: code below is using the manager protocol
        # NOTE: side-effect.. last element to be manage()'d
        #       here actually gets wm focus
        if False:
            #getattr(self,'window_per_channel',True):
            for name, chan in ChannelType.registry.items():
                self.manage(kls=channel_agent_factory(name),
                            name='ChannelAgent:'+name,
                            kls_kargs=ctx)
        # an agent/window that publishes the api via
        # ipython instance, which is embedded in a gtk gui
        from cortex.services.gui.shell import Shell

        self.manage(kls=Shell,
                    kls_kargs=ctx,
                    name='ShellAgent')

        self.load()

from cortex.core.agent import Agent
class Window(Agent, GUI): pass
GUIChild = Window
