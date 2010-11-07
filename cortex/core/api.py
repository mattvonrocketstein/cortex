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
load_service = universe.loadService
def register_service(service):
    """ """
    pass

def load_file(fname, adl=False, python=True):
    """ loads a local file """
    assert os.path.exists(fname), filerror

    if adl:
        raise Exception, "NIY"

    if python:
        universe = {}
        execfile(fname, universe)
        return NamespacePartition(universe).cleaned
