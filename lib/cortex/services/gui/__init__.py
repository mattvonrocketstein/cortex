""" cortex.services.gui
      http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
"""
from cortex.services.terminal import abstract
from cortex.services.gui.parent import GUI
from cortex.core.agent.manager import AgentManager

def __init__(self, **kargs):
    AgentManager.__init__(self,**kargs)
    abstract.ATerminal(self, **kargs)


GUI = type('GUI',
           ( abstract.ATerminal,
             AgentManager, GUI ),
           dict(__init__=__init__))
