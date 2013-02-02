#!/usr/bin/env python
""" go.py: First/second phase init
"""

import os, sys
from optparse import OptionParser

def build_parser():
    p        = OptionParser()
    ao = p.add_option
    ao("-c",'--cmd', dest="command",
       default="", metavar="COMMAND",
       help="same as python -c")
    ao("--gtk",dest="gtk_reactor",
       default=False,action="store_true",
       help="use the gtk-reactor?")
    ao("--test",dest="run_tests",
       default=False,action="store_true",
       help="run cortex unittest suite")
    ao("-u","--universe",dest="universe",
       metavar="UNIVERSE",
       help="Use universe@FILE")
    ao("-v","--verbose",dest="verbose",
       default=False, action='store_true',
       help="extra debugging information")
    ao('--services',dest="services",
       default="", help="services to start")
    ao('--conf',dest="conf",
       default="", help="configuration file to use")
    ao('--client',dest="client",action='store_true',
       default=False, help="api client")
    return p


from cortex.core.util import report, report_if_verbose
class Interpreter(object):
    def __init__(self,fname):
        self.fname = fname

    def namespace(self):
        from cortex.core.universe import Universe
        from cortex.core.agent import Agent
        from cortex.mixins.flavors import ReactorRecursion
        namespace = dict(__universe__=Universe,
                         __file__ = os.path.abspath(self.fname))
        namespace.update(locals())
        namespace.pop('self')
        return namespace

    def ex(self, sandbox):
        execfile(self.fname, sandbox)
        return sandbox

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
    nodeconf_file = options.conf

    #  python interpretter compatability:
    #    shell$ cortex -c"import cortex; print cortex.__file__"
    if args and len(args)==1:
        fname = args[0]
        if os.path.exists(fname):
            print "cortex: assuming this is a file.."
            interpreter = Interpreter(fname)

            sandbox = interpreter.namespace()
            interpreter.ex(sandbox)
            instructions = sandbox.get('__instructions__', [])
            agent_specs = sandbox.get('__agents__', [])
            if instructions and options.conf:
                raise RuntimeError(
                    "cant use '__instructions__' and "
                    "still pass --conf="+options.conf)
            elif not instructions and options.conf:
                sandbox['__universe__'].nodeconf_file = options.conf
            elif instructions and not options.conf:
                sandbox['__universe__'].set_instructions(instructions)

            for agent_spec in agent_specs:
                if isinstance(agent_spec, (list,tuple)):
                    args, kargs = agent_spec
                else:
                    args, kargs = [agent_spec], {}
                sandbox['__universe__'].agents.manage(*args, **kargs)

            if '.play()' not in open(fname).read():
                # FIXME: hack
                report_if_verbose("This file did not start the universe.  allow me")
                sandbox['__universe__'].play()
            report_if_verbose("finished running this universe.")
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
    from cortex.bin.client import use_client
    from cortex.contrib.reloading_helpers import run as RUN
    #Universe.directives = options.directives.split(",")

    # reflect command-line options in universe's config
    olist = [ x for x in dir(options) if not x.startswith('_') \
              and x not in 'read_file read_module ensure_value'.split() ]
    [setattr(Universe.command_line_options, x, getattr(options,x)) for x in olist]
    if options.verbose:
        import cortex
        cortex.VERBOSE = True

    # use the cortex api client?
    if options.client:
        return use_client(options, args)

    #  python interpretter compatability:
    #    shell$ cortex -c"print 3"
    #  NB: comes after options.client because it might want to consume that
    elif options.command:
        exec(options.command)
        return

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
            api.do([['load_service', (s.strip(),), {}]])

    if nodeconf_file:
        verify_file(nodeconf_file)
        install_nodeconf(nodeconf_file, options, args)
        return Universe.play() # Invoke the Universe

def verify_file(f):
    if not os.path.exists(f):
        err='Path "{0}" does not exist.'.format(f)
        print err
        sys.exit()

if __name__ == '__main__':
    entry()
