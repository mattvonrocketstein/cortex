""" cortex.core.api

      TODO: make "alias" decorator
"""

import os, sys
import subprocess
from cortex.core.parsing import Nodeconf
from cortex.core.universe import Universe as universe
from cortex.core.util import report
from cortex.core.hds import HDS

def publish(**kargs):
    """ return a dictionary of the namespace for this module """

    from cortex.core import api
    from cortex.util.namespaces import NamespacePartition

    # inspect this module
    base_api = NamespacePartition(api.__dict__, dictionaries=False)
    extra    = NamespacePartition(dict(publish_kargs=kargs), dictionaries=False)

    publish_services = kargs.get('publish_services', True)
    if publish_services:
        services  = dict( universe.services.items() )
        extra    += services
    out = base_api.cleaned + extra
    return out

def do(instructions, _api=None):
    """ do: execute a set of instructions wrt api <_api> """
    this_api = _api or publish()
    for instruction in instructions:
        name, args, kargs = instruction
        handler = this_api[name]
        # [handler,args,kargs]
        handler(*args, **kargs)

def clone(file=None, nodeconf=None):
    """ """

    # tell the universe to clone itself using the new nodedef
    line = '{shell} "{prog} {args} {file}"&'.format(shell = universe.system_shell,
                                                    file  = file,
                                                    prog  = universe.command_line_prog,
                                                    args  = universe.decide_options())

    # hack to avoid infinite recursion, see also universe.decide_options
    if "do_not_clone" in universe.directives:
        pass
    else:
        p = subprocess.Popen(line, shell=True)
        universe._procs.append(p)

def declare_goals(list_of_callables):
    #list_of_callables
    from cortex.services.goalmonitor import GoalMonitor
    do( [[ "load_service",
          ("GoalMonitor",),
          dict(goals=list_of_callables)  ],])

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

def chat(api, msg=".. answering ping", response='pong!'):
    """ simple command, but very useful for testing remote apis """
    report(msg)
    return response

def build_agent(name, kls=object, kls_kargs={}):
    """ proxy to the agent manager

         TODO: obsoleted by universe.services.__call__ ?
    """
    universe.agents.manage(name=name, kls=kls, kls_kargs=kls_kargs)

ping = chat
echo = chat

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
agents        = universe.agents

register_service = universe.services.register
register_peer    = universe.peers.register
last_peer        = lambda: peers[0]
show_last_peer   = lambda: report('most recent peer',last_peer())
