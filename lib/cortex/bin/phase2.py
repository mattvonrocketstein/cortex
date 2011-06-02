""" cortex.bin.phase2
"""
import os

from cortex.core.universe import Universe
from cortex.core.util import report

def install_nodeconf(nodeconf_file, options, args):
    """ """
    # Set node configuration file in universe
    instance_dir = os.path.split(__file__)[0]
    Universe.instance_dir = instance_dir
    if not os.path.exists(nodeconf_file):
        report("Expected node.conf @ "+nodeconf_file+', None found.')
        Universe.nodeconf_file = None
    else:
        report("Loading with config @ %s" % nodeconf_file)
        Universe.nodeconf_file = nodeconf_file
