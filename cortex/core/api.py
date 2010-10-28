""" cortex.core.api
"""
import os

fileerror = "No such file"

def publish():
    """ return a dictionary of the namespace for this module """
    from cortex.core import api
    from cortex.util.namespaces import NamespacePartition
    return NamespacePartition(api.__dict__).cleaned

def loadfile(fname):
    """ loads a local file """
    assert os.path.exists(fname),filerror
    universe = {}
    exec file in universe
    return universe
