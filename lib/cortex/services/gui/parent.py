from ipython_view import *
from common import CommonInterface
from cortex.services.terminal import abstract
from cortex.core.util import report, console


class GUI(CommonInterface):
    """ """
    def set_shell(self):
        S = self.scrolled_window
        from cortex.core.data import IPY_ARGS
        self.shell = IPythonView(argv=IPY_ARGS,
                        user_ns=abstract.ATerminal .compute_terminal_namespace())

        self.shell.show()
        S.add(self.shell)
        S.show()
        return S

    def really_start(self):
        """ TODO: defer to universe.command_line_options
                  for whether to magic_pdb """
        if not self.universe.config.gtk_reactor==True:
            err  = "This universe isn't configured for GTK reactor, "
            err += "but you're trying to use the gtk terminal!"
            ctx  = str(self)
            self.fault(err, ctx)
            self.universe.stop()

        components  = [ self.spawn_channel_watcher,
                        self.spawn_shell, ]

        for c in components:
            c()
        self.load()

    def spawn_channel_watcher(self):
        from cortex.services.gui.channel_window import ChannelAgent
        self.manage(kls=ChannelAgent, kls_kargs=dict(universe=self.universe),
                    name='ChannelAgent')

    def spawn_shell(self):
        """ interesting.. safe to call multiple times"""
        report('spawns')
        self.manage(kls=Shell, kls_kargs=dict(universe=self.universe), name='ShellAgent')

from cortex.core.agent import Agent
class Window(Agent, GUI): pass
GUIChild = Window

class Shell(Window):
    def start(self):
        window = self.spawn_window
        window.add(self.set_shell())
        window.show()
        self.set_prompt()
