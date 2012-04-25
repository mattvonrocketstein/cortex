""" cortex.bin.client
"""
import os
import sys

from cortex.core.util import report
from cortex.core.universe import Universe
from cortex.core.data import CORTEX_PORT_RANGE
from cortex.core.peer import CortexPeer
from cortex.core import api

def use_client(options, args):
    """
    Invocation of the universe, tailored specifically for calling up
    other universes.  After the TUI bootstraps, the host in question
    has the name 'peer'.  To call a method on the remote host, simply
    run something like 'peer.method(arguments)'

        USAGE:

          # HOST : PORT         COMMAND-LINE
          #################################################
            localhost : 1337      $ cortex --client
            otherHost : 1337      $ cortex --client otherHost
            otherHost : 1337      $ cortex --client otherHost:1337
            otherHost : 1337      $ cortex --client otherHost 1337

    TODO: support --cmd, so this isn't forced to interactive

    """
    PORT_START,PORT_FINISH = CORTEX_PORT_RANGE
    host, port = 'localhost', PORT_START
    if not args: pass # use defaults
    elif len(args)==1:
            if ':' in args[0]: host, port = args[0].split(':')
            else:              host = args[0]
    elif len(args)==2:         host, port = args
    else:
        err = '--client is not sure what to do with these arguments: {0}'
        err = err.format(args)
        return Universe.fault(err)
    return _use_client(host, port, options)

def _use_client(host, port, options):
    """
       1) make the peer, ensure it is available in the TUI
       2) load the services that are required to run the tui
       3) we set everything up by hand; the universe uses nil-config
    """

    report('connecting to ctx://{0}:{1} .. '.format(host, port))
    peer = CortexPeer(addr = host, port = port)
    api.contribute(peer=peer)

    cmd = 'peer.' + options.command if options.command else None
    api.load_services('postoffice _linda'.split())
    Universe.set_nodes([])
    if cmd is None:
        api.load_service('terminal')
    else:
        callback = lambda *args, **kargs: [report(*args, **kargs), Universe.halt()]
        command = lambda peer=peer: eval(cmd).addCallbacks(callback, callback)
        CommandAgent = api.function_to_agent(command)
        Universe.agents.manage(kls=CommandAgent, name='CommandAgent')


    return Universe.play()

def entry():
    """ HACK: modify sys.argv in place and chain back to cortex proper """
    cmd = sys.argv[0]
    cmd = os.path.join(os.path.dirname(cmd),'cortex')
    if not os.path.exists(cmd):
        sys.exit("could not find cortex in same dir as ctxcl")
    else:
        sys.argv.insert(1,'--client')
    from cortex.bin.go import entry as entry2
    entry2()