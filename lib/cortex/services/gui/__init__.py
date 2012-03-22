""" cortex.services.gui

      see also: http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
"""
from cortex.services.terminal import abstract
from cortex.services.gui.parent import GUI as _GUI
from cortex.core.agent.manager import AgentManager



class GUI(abstract.ATerminal,
          AgentManager, _GUI ):

    def __init__(self, **kargs):
        AgentManager.__init__(self,**kargs)
        abstract.ATerminal(self, **kargs)

    def shell_contribute_to_ns(self, **kargs):
        ipythonview = self.registry['ShellAgent'].obj.shell
        ip = ipythonview.IP
        ip.user_ns.update(**kargs)

#not used anymore?
__init__ = GUI.__init__
