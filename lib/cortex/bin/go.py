""" go.py: Second-phase init

    Scratchpad:


#os.environ['DJANGO_SETTINGS_MODULE'] = ''
#from twisted.internet import reactor
#from twisted.internet import stdio
#from twisted.internet.protocol import Factory
#from cortex.core.rcvr import RCVR
#universe = core.universe


    #from cortex.core.rcvr import FileIOFactory
    #fileio = FileIOFactory({})
    #reactor.listenTCP(1234, fileio)
    #reactor.run()

"""

import os, sys
from optparse import OptionParser

from cortex import core
from cortex.core.universe import Universe
from cortex.core.util import report

NODE_CONF = None #'node.conf'

def build_parser():
    universeHelp = "Use universe@FILE"
    commandHelp = "same as python -c"
    parser = OptionParser()
    parser.add_option("-c",  dest="command", default="", help=commandHelp,  metavar="COMMAND")
    parser.add_option("-u", "--universe", dest="universe",help=universeHelp, metavar="UNIVERSE")
    return parser

def main():
    """ """
    # Set node configuration file in universe
    instance_dir = os.path.split(__file__)[0]
    nodeconf_file = NODE_CONF or os.path.join(instance_dir, 'node.conf')
    Universe.instance_dir = instance_dir
    if not os.path.exists(nodeconf_file):
        report("Expected node.conf @ "+nodeconf_file+', None found.')
        Universe.nodeconf_file = None
    else:
        Universe.nodeconf_file = nodeconf_file

from cortex.core.reloading_helpers import run as RUN

def entry():
    parser = build_parser()
    (options, args) = parser.parse_args()
    if args and len(args)==1:
        fname = args[0]
        if os.path.exists(fname):
            print "cortex: assuming this is a file.."
            execfile(fname)
    elif options.command:
        exec(options.command)
    elif options.universe:
        if not os.path.exists(options.universe):
            print "Path does not exist."
            sys.exit()
        else:
            U = pickle.loads(open(options.universe).read())
            U.play() # Invoke the Universe
    else:
        main()
        RUN() # Invoke the Universe
        s=Universe.play()

if __name__ == '__main__':
    entry()
