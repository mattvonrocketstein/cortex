""" cortex.services.terminal

    Terminal Service:

          a ipython console TUI
"""
from cortex.services.terminal import abstract
from cortex.services.terminal.shell import ShellAspect
from cortex.core.data import EVENT_T
from cortex.services.api import CORTEX_API_UPDATE_T

class Terminal(shell.ShellAspect, abstract.ATerminal):
    class Meta:
        subscriptions = { EVENT_T : 'push_q',
                          CORTEX_API_UPDATE_T: 'contribute_to_api' }
