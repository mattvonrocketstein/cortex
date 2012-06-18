""" cortex.core.universe

      The universe is an abstraction intended to unify the representation
      of aspects of the interpretter, the operating system, the "mainloop",
      the process, and the cortex runtime.  It should effectively be a
      singleton-- one per process.
"""
import os, sys
import platform, pprint, StringIO

from cortex.core.hds import HDS
from cortex.core.reloading import AutoReloader
from cortex.services import SERVICES
from cortex.core.util import report
from cortex.mixins import AutonomyMixin, Controllable
from cortex.mixins import PersistenceMixin
from cortex.core.peer import PEERS
from cortex.core.agent import AGENTS
from cortex.mixins import OSMixin, PIDMixin
from cortex.core.notation import UniverseNotation
from cortex.mixins import FaultTolerant
from .reactor import ReactorAspect

from cortex.core.universe.node_reader import NodeConfAspect
from cortex.core.universe.servicing import ServiceAspect


from collections import defaultdict

class Tracking(object):
    """ topologies for connective tissue """
    agents        = AGENTS
    services      = SERVICES

    peers         = PEERS
    ports         = defaultdict(lambda: [])     # map ports -> agent

    def declare_peer(self, peer, agent):
        """ """
        peer._agent = agent
        self.ports[peer.port].append(agent)

    def peer2agent(self, peer):
        # TODO: this is an agentizer.. move it to api?
        return self.ports[peer.port]

    def children(self):
        """ """
        return self.agents.children() + self.services.children()

class __Universe__(Tracking,
                   AutoReloader,
                   ServiceAspect,
                   UniverseNotation,
                   OSMixin, PIDMixin,
                   ReactorAspect, Controllable,
                   FaultTolerant, NodeConfAspect,
                   AutonomyMixin, PersistenceMixin,):
    """
    """
    # TODO: clones,processes = CloneManager(), ProcessManager()



    nodeconf_file = u''
    config        = HDS()
    parent        = None # agent.__init__ never called?

    def load(self):
        """ call load for all embedded managers """
        self.services.load()
        self.agents.load()

    def play(self):
        """ entry point.  this guy does not return """
        # report("Universe.play!")
        self.decide_name()
        self.started = True
        from cortex.core import api as API
        from cortex.core.api import publish
        _api = publish()

        def parse_error(error, instruction, args, kargs, api=_api):
            api_header = "Cortex-API @ {H}://{F}"
            api_header = api_header.format(F=API,
                                           H=platform.node(),)
            fhandle    = StringIO.StringIO();
            pprint.pprint(api, fhandle)
            opts   = dict(api=api_header, instruction=instruction,args=args,kargs=kargs)
            header = "ParseError: {E}:".format(E=error)
            body   = ("instruction = {instruction}\n"
                      "args        = {args}\n"
                      "kargs       = {kargs}\n"
                      "with api    = {api}\n")
            error  = (header + body).format(**opts)
            report(error)
            sys.exit()

        def get_handler(instruction):
            """ grab an item named "instruction" from the api """
            return _api.get(instruction)

        # Interprets all the instructions in the nodeconf
        for node in self.Nodes:
           original = node
           instruction, args = node[0], node[1:]
           #report("parsing node", node)
           if len(args) == 1:
               kargs = {}
           else:
               args = args[ : -1 ]
               kargs = (args and args[-1]) or {}

           handler = get_handler(instruction)
           if not handler:
               parse_error("No instruction handler!", instruction, args, kargs)
           handler(*args, **kargs)

        # is this working?
        for name, kls, kls_kargs in self.agents._pending:
            kls_kargs.update( { 'universe' : self } )

        # Call load for all embedded managers
        self.load()

        # Setup threadpool
        self.threadpool = self.getThreadPool()

        # Main loop
        self.reactor.run()


    def sleep(self):
        """
            TODO: send a better signal and use os/pid mixins.
        """
        self.fault(" sleep will be deprecated ")
        self.stop()
        for pid in self.pids['children']:
            os.system('kill -KILL ' + str(pid))
        # self.persist()

    def halt(self):
        """ override from Controllable

            sometimes the universe needs to have it's shutdown triggered by another
            agent, for example when the terminal agent received control-D.  in those
            circumstances, until there is a signal for this, the caller should
            *always* use halt instead of 'stop'.
        """
        #from cortex.core.util import getcaller
        #report('shutting down at the request of:'); print getcaller()
        return self.reactor.callFromThread(self.stop)

    def stop(self):
        """ override autonomy """
        if not self.started:
            return
        self.started = False
        stopped = []

        def failure_stopping_agent(service, e):
            err_msg = ('Squashed exception stopping agent'
                       ' "' + str(service) + '".  '
                       'Original Exception follows')

            report(err_msg)
            report(str(e))
            raise e

        ## stop any other agents
        for agent in set(self.agents.values() + self.services.values()):
            try:
                agent.stop()
                stopped.append(agent)
            except Exception,e:
                failure_stopping_agent(agent, e)

        # we have to check first,
        # maybe bootstrap didn't even get this far
        if hasattr(self,'threadpool'):
            self.threadpool.stop()

        for thr in self.threads:
            thr._Thread__stop()

        import twisted
        try:
            self.reactor.stop()
        except twisted.internet.error.ReactorNotRunning:
            pass
        report("Stopped: ", [x for x in stopped] )

    def decide_name(self):
        """ the universe should never be explicitly named, a universe
            should derive it's own
        """
        name_args = dict( alfa    = str(id(self)),
                          bravo   = getattr(self,'bravo', ''),
                          charlie = getattr(self,'charlie',''),
                          delta   = self.hostname,)
        name = 'Universe({alfa})[{bravo}:{charlie}]@{delta}'.format(**name_args)
        self.name    = name
        return name

# A cheap singleton
Universe = __Universe__()

# Set all the back-refs
AGENTS.universe   = Universe
PEERS.universe    = Universe
SERVICES.universe = Universe