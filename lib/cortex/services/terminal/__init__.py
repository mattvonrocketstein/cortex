""" cortex.services.terminal

    Terminal Service:

          a ipython console TUI
"""
from cortex.services.terminal import abstract
from cortex.services.terminal.shell import ShellAspect

Terminal = type('Terminal', (shell.ShellAspect,abstract.ATerminal), {})
