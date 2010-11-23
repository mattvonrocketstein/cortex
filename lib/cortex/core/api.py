""" cortex.core.api
"""

import os, sys

from cortex.core.parsing import Nodeconf
from cortex.core.universe import Universe as universe
from cortex.core.util import report
from cortex.core.hds import HDS

def publish(**kargs):
    """ return a dictionary of the namespace for this module """

    from cortex.util.namespaces import NamespacePartition

    # import this module and inspect it
    from cortex.core import api
    base_api = NamespacePartition(api.__dict__, dictionaries=False)
    extra    = NamespacePartition(dict(publish_kargs=kargs), dictionaries=False)

    publish_services = kargs.get('publish_services', True)
    if publish_services:
        services  = dict(universe.services.items())
        extra    += services
    out=base_api.cleaned + extra
    return out

def clone():
    """ """


    # to avoid infinite recursion, compute the nodeconf file
    #  that booted this universe, subtracting the "clone" instruction
    nodeconf = Nodeconf(universe.nodeconf_file).parse(ignore=['clone'])

    # put an updated version back together and write it down
    tmp = Nodeconf(None, list=nodeconf)
    x=universe.tmpfile(); tmp.write(x.name); x.close()

    # tell the universe to clone itself using the new nodedef
    return universe^x.name

def load_file(fname, adl=False, python=True):
    """ loads a local file
          known formats:
            python code
            agent description language
            node configuration file format
    """
    from cortex.util.namespaces import NamespacePartition
    fileerror = "No such file"
    assert os.path.exists(fname), filerror

    # handler for agent description language
    if adl:
        raise Exception, "NIY"

    # handler for problem description language
    if pdl:
        raise Exception, "NIY"

    # handler for python file
    if python:
        universe = {}
        execfile(fname, universe)
        return NamespacePartition(universe).cleaned
def resolve(name):
    """ resolve dns names via reactor """
    return universe.reactor.resolve(name).addCallbacks(report,report)

def ping(*args, **kargs):
    """ simple command, but very useful for testing remote apis """
    report(" .. answering ping")
    return 'pong!'

ctx = HDS()
s   = HDS()
s.api = 'api'
#c.api          = (universe|s.api)

# Shortcuts into the Universe
load_service = universe.loadService
sleep        = universe.sleep

# Managers and shortcuts into the managers
services     = lambda: list(universe.services)
peers        = universe.peers

register_service = universe.services.register
register_peer    = universe.peers.register
last_peer        = lambda: peers[0]
show_last_peer   = lambda: report('most recent peer',last_peer())
