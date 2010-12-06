#!/usr/bin/env python
""" go.py: Second-phase init

    Example usage follows:

      $ go chat.py # First looks in

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
from cortex.core.reloading_helpers import run as RUN

# TODO: make a place to unify all the "config" objects
class defaults:
    """ default configuration container, used at runtime for
        cortex bootstrap.  see also cortex.bin.go
    """

    working_directory      = os.path.realpath(os.getcwd())
    system_prefix          = sys.prefix
    nodeconf_file          = "UNLESS OVERRIDEN, DETERMINED JIT"
    cortex_system_etc      = os.path.join(system_prefix,"etc")
    demo_dir               = os.path.join(cortex_system_etc,"demos")
    default_nodeconf_file  = os.path.join('etc', 'node.conf')

    def decide_nodeconf_file(self):
        from cortex.util.logic import first

        sys_nodeconf_file      = os.path.join(defaults.system_prefix,
                                              defaults.default_nodeconf_file)

        relative_nodeconf_file = os.path.join(defaults.working_directory,
                                              defaults.default_nodeconf_file)
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
        report("node.conf @ "+nodeconf_file+' not found.. checking in')
        Universe.nodeconf_file = None
    else:
        report("Loading with config @ %s" % nodeconf_file)
        Universe.nodeconf_file = nodeconf_file


def run_file(fname):
    """ is it more comfortable for user if
        we add a "Universe.play()" here?
    """
    scope = globals().copy()
    scope.update(dict(__file__ = os.path.abspath(fname)))
    try:
        execfile(fname,scope)
    except Exception,e:
        scope.update(dict(__exception__=e))
        return False, scope
    else:
        return True, scope

def handle_file(args):
    """ search order:
          1. if absolute, or starts with ./, then don't look anywhere else
          2. look and see if it's a file relative
          3. look and see if it's a demo named in <node_root>/etc/demos
    """
    fname                     = args[0]
    fname_as_demo             = (not fname.startswith(os.path.sep) and \
                                 not fname.startswith('./')) and \
                                os.path.join(defaults.demo_dir, fname)
    fname_as_relative_to_root = (not fname.startswith(os.path.sep) and \
                                 not fname.startswith('./')) and \
                                os.path.join(defaults.system_prefix, fname)

    if os.path.exists(fname):                       pass
    elif os.path.exists(fname_as_relative_to_root): fname=fname_as_demo
    elif os.path.exists(fname_as_demo):             fname=fname_as_demo

    else:
        raise Exception,"Not sure what to do with the argument {arg}, expected a filename or something.".format(arg=fname)
    print ' '.join(sys.argv)
    print "cortex: assuming this is a file.."
    return fname

def embed_shell(**kargs):
    # TODO: change this to use cortex.core.terminal if not
    #       cortex.services.terminal
    import IPython
    embedshell = IPython.Shell.IPShellEmbed(argv=['-noconfirm_exit'],user_ns=kargs)
    embedshell()

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
            success, scope = run_file(handle_file(args))
            if not success:
                if options.interactive:
                    report("Caught exception while executing", args)
                    report('  Original exception will be availible as "__exception__", details follow:',exception=scope.get('__exeption__'))
                    embed_shell(**scope)
                else:
                    raise Exception, scope['__exception__']

    elif options.interactive: embed_shell()
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
