""" cortex.core.api
"""
import os
from cortex.util.namespaces import NamespacePartition

fileerror = "No such file"

def publish():
    """ return a dictionary of the namespace for this module """
    from cortex.core import api
    return NamespacePartition(api.__dict__).cleaned

def loadfile(fname, adl=False, python=True):
    """ loads a local file """
    assert os.path.exists(fname), filerror

    if adl:
        raise Exception, "NIY"

    if python:
        universe = {}
        execfile(fname, universe)
        return NamespacePartition(universe).cleaned
