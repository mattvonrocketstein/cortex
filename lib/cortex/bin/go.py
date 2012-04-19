#!/usr/bin/env python
""" go.py: First/second phase init
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
    testHelp      = "run cortex unittest suite"
    clientHelp    = "api client"
    p        = OptionParser()
    p.add_option("-c",dest="command",default="",help=commandHelp,  metavar="COMMAND")
    p.add_option("--gtk",dest="gtk_reactor", default=False,action="store_true",help=gtkHelp)
    p.add_option("--test",dest="run_tests", default=False,action="store_true", help=testHelp)
    p.add_option("-u","--universe",dest="universe",help=universeHelp, metavar="UNIVERSE")
    p.add_option('--directives',dest="directives", default="", help=directiveHelp)
    p.add_option('--services',dest="services", default="", help=directiveHelp)
    p.add_option('--conf',dest="conf",default=REL_NODE_CONF, help=confHelp)
    p.add_option('--client',dest="client",action='store_true',default=False,help=clientHelp)
    return p

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

    #  python interpretter compatability:
    #    shell$ cortex -c"import cortex; print cortex.__file__"
    if args and len(args)==1:
        fname = args[0]
        if os.path.exists(fname):
            print "cortex: assuming this is a file.."
            __file__ = os.path.abspath(fname)
            execfile(fname)
            return

    #  python interpretter compatability:
    #    shell$ shell$ cortex somefile
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
    from cortex.bin.phase2 import use_client
    from cortex.core.reloading_helpers import run as RUN
    Universe.directives = options.directives.split(",")

    # reflect command-line options in universe's config
    olist = [ x for x in dir(options) if not x.startswith('_') \
              and x not in 'read_file read_module ensure_value'.split() ]
    [setattr(Universe.config,x,getattr(options,x)) for x in olist]

    # use the cortex api client?
    if options.client:
        return use_client(args)

    # run tests?
    if options.run_tests:
        from cortex.tests import main
        return main()

    # deserialize a saved universe and resume it?
    if options.universe:
        verify_file(options.universe)
        U = pickle.loads(open(options.universe).read())
        return U.play() # Invoke the Universe


    ## After this point it's assumed we're using a node-conf,
    ## whether it is specified explicitly or assumed.  the cases for
    ## the command-line options should not use 'return'

    # augment nodeconf with additional services?
    if options.services:
        from cortex.core import api
        services = options.services.split(',')
        for s in services:
            api.do([['load_service', (s,), {}]])
    verify_file(nodeconf_file)
    install_nodeconf(nodeconf_file, options, args)
    return Universe.play() # Invoke the Universe

def verify_file(f,err="Path does not exist."):
    if not os.path.exists(f):
        print err
        sys.exit()

if __name__ == '__main__':
    entry()
