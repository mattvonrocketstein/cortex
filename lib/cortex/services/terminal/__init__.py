""" cortex.services.terminal

    Terminal Service:
          an ipython console that uses the cortex api

            <start>: a few words about starting
            <stop>:  a few words about stopping

"""
from cortex.core.util import report, console
from cortex.services.terminal import abstract
from cortex.services.terminal.shell import ShellAspect
from cortex.services.terminal._gtk import GUI

Terminal = type('Terminal', (abstract.ATerminal, shell.ShellAspect), {})
#Terminal = type('Terminal', (abstract.ATerminal, _gtk.GUI), {})
