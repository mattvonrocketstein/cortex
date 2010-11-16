""" cortex.core.api
"""
import os
from cortex.util.namespaces import NamespacePartition
from cortex.core.universe import Universe as universe

fileerror = "No such file"


def publish():
    """ return a dictionary of the namespace for this module """
    from cortex.core import api
    return NamespacePartition(api.__dict__).cleaned

def register_service(service):
    """ """
    pass

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
services     = lambda: list(universe.services)
load_service = universe.loadService
sleep        = universe.sleep
peers        = universe.peers

def last_peer():
    return peers[peers[0]]
def show_last_peer():
    print last_peer()