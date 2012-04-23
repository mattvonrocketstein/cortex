""" cortex.bin.phase2

    helpers for cortex.bin.go, the main commandline entry point.

    all time-sensitive bootstrapping should be finished by now.
    phase2 is by definition a place where it is safe to import cortex.
"""
import os

from cortex.core.universe import Universe
from cortex.core.util import report
from cortex.core.data import CORTEX_PORT_RANGE
from cortex.core.peer import CortexPeer
from cortex.core import api

def install_nodeconf(nodeconf_file, options, args):
    """ bootstraps universe using a file with a list
        of instructions.

         USAGE:
           cortex --conf=etc/node_definition.conf
    """
    instance_dir = os.path.split(__file__)[0]
    Universe.instance_dir = instance_dir
    if not os.path.exists(nodeconf_file):
        report("Expected node.conf @ "+nodeconf_file+', None found.')
        Universe.nodeconf_file = None
    else:
        report("Loading with config @ %s" % nodeconf_file)
        Universe.nodeconf_file = nodeconf_file
