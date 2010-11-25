#!/usr/bin/env python
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
    parser.add_option("-x",  '--xterm', dest="xterm", action="store_true", default=False,
                      help=commandHelp,  metavar="XTERM")
    parser.add_option("-c",  dest="command", default="", help=commandHelp,  metavar="COMMAND")
    parser.add_option("-u", "--universe", dest="universe",help=universeHelp, metavar="UNIVERSE")
    parser.add_option('--conf', dest="conf", default=os.path.join(
                                                 os.path.realpath(os.getcwd()),
                                                 'etc',
                                                 'node.conf'
                                             ),
                      help="Config to use [default: %default]"
                      )
    return parser

def install_nodeconf(nodeconf_file, options, args):
    """ """
    # Set node configuration file in universe
    instance_dir = os.path.split(__file__)[0]
    Universe.instance_dir = instance_dir
    if not os.path.exists(nodeconf_file):
        report("Expected node.conf @ "+nodeconf_file+', None found.')
        Universe.nodeconf_file = None
    else:
        report("Loading with config @ %s" % nodeconf_file)
        Universe.nodeconf_file = nodeconf_file

from cortex.core.reloading_helpers import run as RUN

def entry():
    """
    elif options.xterm:
        xterm = Universe.has_command('xterm')
        if xterm:
            ncf  = Universe.nodeconf_file
            clo  = Universe.command_line_invocation
            tmp  = clo.replace(' --xterm', ' ').replace(' --x',' ').replace(' -x',' ')
            line = xterm+' -fg green -bg black -e "' + tmp + '"&'
            print 'running:'
            print '\t'+line
            os.system(line)
    """

    parser = build_parser()
    (options, args) = parser.parse_args()
    nodeconf_file = NODE_CONF or options.conf
    if args and len(args)==1:
        fname = args[0]
        if os.path.exists(fname):
            print "cortex: assuming this is a file.."
            __file__ = fname
            execfile(fname)
            #Universe.play()

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
        install_nodeconf(nodeconf_file, options, args)
        RUN() # Invoke the Universe
        s=Universe.play()

if __name__ == '__main__':
    entry()
