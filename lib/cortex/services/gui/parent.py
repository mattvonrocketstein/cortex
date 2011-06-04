""" cortex.services.gui.parent
"""
from ipython_view import *
from common import CommonInterface
from cortex.services.terminal import abstract
from cortex.core.util import report, console

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

    def really_start(self):
        """ TODO: defer to universe.command_line_options
                  for whether to magic_pdb
        """
        if not self.universe.config.gtk_reactor==True:
            err  = "This universe isn't configured for GTK reactor, "
            err += "but you're trying to use the gtk terminal!"
            ctx  = str(self)
            self.fault(err, ctx)
            self.universe.stop()


        from cortex.services.gui.channel_window import ChannelAgent
        from cortex.services.gui.shell import Shell

        components  = [
            dict(kls=ChannelAgent,
                 kls_kargs=dict(universe=self.universe),
                 name='ChannelAgent'),
            dict(kls=Shell,
                kls_kargs=dict(universe=self.universe),
                 name='ShellAgent')
            ]

        for c in components:
            self.manage(**c)
        self.load()


    def spawn_shell(self):
        """ interesting.. safe to call multiple times"""
        report('spawns')


from cortex.core.agent import Agent
class Window(Agent, GUI): pass
GUIChild = Window
