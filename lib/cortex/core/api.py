""" cortex.core.api
"""
import os
from cortex.util.namespaces import NamespacePartition
from cortex.core.universe import Universe as universe
from cortex.core.util import report

fileerror = "No such file"

def publish():
    """ return a dictionary of the namespace for this module """
    from cortex.core import api
    return NamespacePartition(api.__dict__).cleaned


def load_file(fname, adl=False, python=True):
    """ loads a local file

          known formats:
            python code
            agent description language
            node configuration file format
    """
    assert os.path.exists(fname), filerror

    if adl:
        raise Exception, "NIY"

    if python:
        universe = {}
        execfile(fname, universe)
        return NamespacePartition(universe).cleaned

def ping(*args, **kargs):
    """ """
    print "answering ping"
    return 'pong', args, kargs

# Shortcuts into the Universe
load_service = universe.loadService
sleep        = universe.sleep

# Managers and shortcuts into the managers
services     = lambda: list(universe.services)
peers        = universe.peers
register_service = universe.services.register
register_peer = universe.peers.register

def last_peer():
    return peers[peers[0]]
def show_last_peer():
    print last_peer()
