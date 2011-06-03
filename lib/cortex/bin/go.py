#!/usr/bin/env python
""" go.py: Second-phase init
"""

import os, sys
from optparse import OptionParser

ABS_NODE_CONF = '/etc/cortex/node.conf'
ABS_NODE_CONF = os.path.exists(ABS_NODE_CONF) and ABS_NODE_CONF or None
REL_NODE_CONF = os.path.join(os.path.realpath(os.getcwd()),
                             'etc', 'node.conf')

def build_parser():
    nodeHelp      = "Config to use [default: %default]"
    universeHelp  = "Use universe@FILE"
    directiveHelp = "Directives"
    confHelp      = "Node configuration file to use"
    commandHelp   = "same as python -c"
    gtkHelp       = "use the gtk-reactor?"
    parser        = OptionParser()

    #parser.add_option("-x",  '--xterm', dest="xterm", action="store_true", default=False,
    #                  help=commandHelp,  metavar="XTERM")
    parser.add_option("-c",     dest="command", default="", help=commandHelp,  metavar="COMMAND")
    parser.add_option("--gtk",  dest="gtk_reactor", default=False, action="store_true", help=gtkHelp)
    parser.add_option("-u", "--universe", dest="universe",help=universeHelp, metavar="UNIVERSE")
    parser.add_option('--directives', dest="directives", default="", help=directiveHelp)
    parser.add_option('--conf', dest="conf", default=REL_NODE_CONF, help=confHelp)
    return parser

def entry():
    """
    """
    ## Phase 1:
    ##  cortex should not have been imported anywhere, so
    ##  we should not have already chosen a twisted reactor.
    ##  do as much as we can before importing anything else,
    ##  to keep the bootstrap sacred
    parser        = build_parser()
    options, args = parser.parse_args()
    nodeconf_file = ABS_NODE_CONF or options.conf or REL_NODE_CONF

    #  python interpretter compatability, coverage usage like:
    #   shell$ cortex -c"import cortex; print cortex.__file__"
    #   shell$ cortex somefile
    if args and len(args)==1:
        fname = args[0]
        if os.path.exists(fname):
            print "cortex: assuming this is a file.."
            __file__ = os.path.abspath(fname)
            execfile(fname)
            return
    elif options.command:
        exec(options.command)
        return

    # use the gtk-reactor?
    if options.gtk_reactor:
        print "using gtk reactor"
        from twisted.internet import gtk2reactor # for gtk-2.0
        gtk2reactor.install()


    ## Phase 2:
    ##  trigger the first cortex imports.
    ##  there goes the neighborhood.
    from cortex.core.universe import Universe
    from cortex.bin.phase2 import install_nodeconf
    from cortex.core.reloading_helpers import run as RUN
    Universe.directives = options.directives.split(",")

    # mirror command-line options in universe's config
    olist = [x for x in dir(options) if not x.startswith('_') and x not in 'read_file read_module ensure_value'.split()]
    [setattr(Universe.config,x,getattr(options,x)) for x in olist]

    ## deserialize a saved universe and resume it
    if options.universe:
        if not os.path.exists(options.universe):
            print "Path does not exist."
            sys.exit()
        else:
            U = pickle.loads(open(options.universe).read())
            U.play() # Invoke the Universe
        return

    # Otherwise install the nodeconf that we found and run it.
    install_nodeconf(nodeconf_file, options, args)
    RUN() # Invoke the Universe
    s=Universe.play()

if __name__ == '__main__':
    entry()
