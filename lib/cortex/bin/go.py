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

from cortex import core
from cortex.core.universe import Universe
from cortex.core.util import report

# TODO: make a place to unify all the "config" objects
class defaults:
    """ default configuration container, used at runtime for
        cortex bootstrap.  see also cortex.bin.go
    """
    working_directory = os.path.realpath(os.getcwd())
    system_prefix     = sys.prefix
    nodeconf_file     = "UNLESS OVERRIDEN, DETERMINED JIT"

    def decide_nodeconf_file(self):
        from cortex.util.logic import first
        default_nodeconf_file  = os.path.join('etc', 'node.conf')
        sys_nodeconf_file      = os.path.join(defaults.system_prefix, default_nodeconf_file)
        relative_nodeconf_file = os.path.join(defaults.working_directory, default_nodeconf_file)
        # TODO: read user/site-specific config here..
        options = [relative_nodeconf_file, sys_nodeconf_file ]
        options = [option for option in options if os.path.exists(option)]
        self.nodeconf_file = first(options, predicate=os.path.exists)
        return self.nodeconf_file
defaults = defaults()
defaults.decide_nodeconf_file()

def build_parser():
    
    from optparse import OptionParser
    class Help(object):
        universeHelp     = "Use universe@FILE"
        labelHelp        = 'Label for universe (useful with "ps aux")'
        directiveHelp    = "Directives"
        commandHelp      = "same as python -c"
        interactiveHelp  = "similar to python -i"
        configHelp       = "Config to use [default: %default]"

    parser        = OptionParser()
    parser.add_option("-x",  '--xterm', dest="xterm", action="store_true",
                      default=False, help=Help.commandHelp,  metavar="XTERM")
    parser.add_option("-i", '--interactive', dest="interactive", default=False,
                      action="store_true", help=Help.interactiveHelp,  metavar="COMMAND")
    parser.add_option("-c",  dest="command", default="", help=Help.commandHelp,
                      metavar="COMMAND")
    parser.add_option("--label",  dest="label", default="NOLABEL",
                      help=Help.labelHelp,  metavar="LABEL")
    parser.add_option("-u", "--universe", dest="universe",
                      help=Help.universeHelp, metavar="UNIVERSE")
    parser.add_option('--directives', dest="directives",
                      default="", help=Help.directiveHelp)
    parser.add_option('--conf', dest="conf",
                      default=defaults.nodeconf_file, help=Help.configHelp)
    return parser

def install_nodeconf(nodeconf_file, options, args):
    """ """
    # Set node configuration file in universe
    instance_dir          = os.path.split(__file__)[0]
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

    parser        = build_parser()
    options, args = parser.parse_args()
    nodeconf_file       = options.conf
    Universe.label      = options.label
    Universe.directives = options.directives.split(",")
    if args and len(args)==1:
        fname = args[0]
        if os.path.exists(fname):
            print "cortex: assuming this is a file.."
            __file__ = os.path.abspath(fname)
            execfile(fname)
            #Universe.play()
    elif options.interactive:
        # TODO: change this to use cortex.core.terminal if not
        #       cortex.services.terminal
        import IPython
        embedshell = IPython.Shell.IPShellEmbed(argv=['-noconfirm_exit'])
        embedshell()

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
