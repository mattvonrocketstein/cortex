""" cortex.core.api

      TODO: make "alias" decorator
      NB: unused imports in this file are normal and desirable
"""

import os, sys
import subprocess

from goulash import Namespace

from cortex.core.parsing import Nodeconf
from cortex.core.universe import Universe as universe
from cortex.core.util import report
from cortex.core.hds import HDS

def msg(name,content):
    poffice = (universe|'postoffice')
    chan = getattr(poffice, name)
    chan(content)

def function_to_agent(func, return_bus=None):
    """ TODO: revisit this
              it doesnt have to be threaded,
              and there are other agentizers scattered around
    """
    from cortex.mixins.flavors import Threaded
    return Threaded.from_function(func, return_bus=None)

def contribute(**namespace):
    """ cortex.core.api.contribute()

        simply adds a function to the namespace of the module
        ``cortex.core.api``.  this may not affect any agents who
        have already acted on the basis of the contents of that
        module.  to request that those agents update, you need to
        do something like this:

           >>> from cortex.core.data import CORTEX_API_UPDATE_T
           >>> postoffice = (universe|'postoffice')
           >>> postoffice.publish(CORTEX_API_UPDATE_T,**namespace)
    """
    from cortex.core import api
    for k,v in namespace.items():
        if k in dir(api):
            raise ValueError,"{0} is already in the API.".format(k)
        else:
            setattr(api, k, v)

def publish(**kargs):
    """ return a dictionary of the namespace for this module,
        after a small bit of postprocessing.

        NOTE: in general the result of this operation is not serializable,
              because it contains the universe itself..
    """

    from cortex.core import api
    # inspect this module
    base_api = Namespace(api.__dict__, dictionaries=False)
    extra    = Namespace(dict(publish_kargs=kargs), dictionaries=False)

    publish_services = kargs.get('publish_services', True)
    if publish_services:
        services  = dict( universe.services.items() )
        extra    += services
    out = base_api.nonprivate + extra
    return out

def api_names(): return sorted(publish().keys())

def do(instructions, _api=None):
    """ do: execute a set of instructions wrt api <_api> """
    this_api = _api or publish()

    def unpack(i):
        ''' potentially unserialize/deencrypt, etc '''
        try:
            name, args, kargs = i
        except ValueError:
            raise Exception,"Error unpacking instruction: "+str(i)
        return name,args,kargs

    for instruction in instructions:
        name, args, kargs = unpack(instruction)
        handler = this_api[name]
        handler(*args, **kargs)

def clone(file=None, nodeconf=None):
    """ makes a clone of this universe as a subprocess.

        the original universe will be able to pass messages
        back and forth with the clone.. if you're using the
        network-mapper service, the new universe should be
        discovered automatically and added to the peer list.
    """

    # tell the universe to clone itself using the new nodedef
    system_shell  = 'xterm -fg green -bg black -e '
    options = "--directives=do_not_clone"
    line = '{shell} "{prog} {args} {file}"&'.format(shell = system_shell,
                                                    file  = file,
                                                    prog  = universe.command_line_prog,
                                                    args  = options)

    # hack to avoid infinite recursion, see also universe.decide_options
    if "do_not_clone" in universe.directives:
        pass
    else:
        p = subprocess.Popen(line, shell=True)
        universe._procs.append(p)

def declare_goals(list_of_callables):
    """ loads without waiting a specific instruction
        that wakes up the goal-monitor.  the universe
        will stop when all the goals are complete.
    """
    from cortex.services.goalmonitor import GoalMonitor
    do( [[ "load_service",
          ("GoalMonitor",),
          dict(goals=list_of_callables)  ],])

def load_file(fname, adl=False, pdl=False, python=True):
    """ loads a local file
          known formats:
            python code
            agent description language
            node configuration file format
    """
    fileerror = "No such file"
    assert os.path.exists(fname), fileerror

    # handler for agent description language
    # handler for problem description language
    if adl: raise Exception, "NIY"
    if pdl: raise Exception, "NIY"

    # handler for python file
    if python:
        universe = {}
        execfile(fname, universe)
        return Namespace(universe).nonprivate

def resolve(name):
    """ resolve dns names via reactor """
    return universe.reactor.resolve(name).addCallbacks(report,report)

def chat(api, msg=".. answering ping", response='pong!'):
    """ simple command, but very useful for testing remote apis """
    if msg:
        report(msg)
    return response

def build_agent(name, kls=object, kls_kargs={}):
    """ proxy to the agent manager

         TODO: obsoleted by universe.services.__call__ ?
    """
    universe.agents.manage(name=name, kls=kls, kls_kargs=kls_kargs)

def is_cortex(msg): return msg
def ping():         return chat('ping')

# Shortcuts into the Universe
load_service = universe.loadService
load_services = universe.loadServices
load_agent = universe.loadAgent
#sleep        = universe.sleep

# Managers and shortcuts into the managers
services     = lambda: list(universe.services)
peers        = universe.peers
agents        = universe.agents

register_service  = universe.services.register
register_peer     = universe.peers.register
last_peer         = lambda: peers[0]
declare_agent     = universe.agents
load_instructions = do

class cortex:
    @property
    def channels(self):
        from channel import ChannelType
        return ChannelType.registry
cortex=cortex()
