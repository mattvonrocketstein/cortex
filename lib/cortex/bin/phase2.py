""" cortex.bin.phase2

    helpers for cortex.bin.go, the main commandline entry point.

    all time-sensitive bootstrapping should be finished by now.
    phase2 is by definition a place where it is safe to import cortex.
"""
import os

from cortex.core.universe import Universe
from cortex.core.util import report
from cortex.core.data import CORTEX_PORT_RANGE
from cortex.core.peer import CortexPeer
from cortex.core import api

def install_nodeconf(nodeconf_file, options, args):
    """ bootstraps universe using a file with a list
        of instructions.

         USAGE:
           cortex --conf=etc/node_definition.conf
    """
    instance_dir = os.path.split(__file__)[0]
    Universe.instance_dir = instance_dir
    if not os.path.exists(nodeconf_file):
        report("Expected node.conf @ "+nodeconf_file+', None found.')
        Universe.nodeconf_file = None
    else:
        report("Loading with config @ %s" % nodeconf_file)
        Universe.nodeconf_file = nodeconf_file

def use_client(args):
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
    return _use_client(host, port)

def _use_client(host, port):
    """
       1) make the peer, ensure it is available in the TUI
       2) load the services that are required to run the tui
       3) we set everything up by hand; the universe uses nil-config
    """
    report('connecting to ctx://{0}:{1} .. '.format(host, port))
    peer = CortexPeer(addr = host, port = port)
    api.contribute(peer=peer)
    api.load_services('postoffice _linda terminal'.split())
    Universe.set_nodes([])
    return Universe.play()
