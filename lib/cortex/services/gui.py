""" cortex.services.gui
      http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
"""

from cortex.services.terminal import abstract
from cortex.services.terminal.shell import ShellAspect
from cortex.services.terminal._gtk import GUI

GUI = type('GUI', (abstract.ATerminal, GUI), {})
