""" example boot script for cortex
"""

from cortex.core import api
from cortex.core.util import report
from cortex.core.universe import Universe
from cortex.core.node import Agent, TaskList


class Chat(Agent):
    """ """

    def input_proc(self, *args, **kargs):
        """ """
        txt=args[0]
        if txt.strip().startswith('#'):
                #report('----> chatting', args, kargs)
                for name,peer in self.universe.peers.items():
                    if 'self' != peer.host:
                        peer.api.chat( txt + ' -- '+self.universe.name)

                ( self.universe|'postoffice' ).publish('chat', args[0])
        else:
            self.original_input_processor(*args, **kargs)
        #return False

    def setup(self):
        terminal = (self.universe|'terminal')
        ( self.universe|'api' ).augment_with(chat=self.rcv_chat)
        self.original_input_processor= terminal.get_input_processor() #self.shell.IP.runsource

        # When lines start with '#', treat them as a chat message.
        old_proc = terminal.replace_input_processor(self.input_proc)

        # quiet down the usual terminal event messages
        terminal.syndicate_events = False

    def xmt_chat(self, msg):
        ( self.universe|'postoffice' ).publish('chat', msg)

    def rcv_chat(self, postoffice, *args, **kargs):
        print args[0]
        #report(postoffice, args, **kargs)

    def iterate(self):
        pass
        #( self.universe|'postoffice' ).subscribe('chat', self.rcv_chat)

# Load services
api.do( [
        [ "load_service", ("api",),            {} ],
        [ "load_service", ("_linda",),         {} ],
        [ "load_service", ("terminal",),       {} ],
        [ "load_service", ("postoffice",),     {} ],
        [ "load_service", ("network_mapper",), {} ],
        ])

api.do([ ["build_node", ('test-node',), dict(kls=Chat, kls_kargs={'name':'chat-agent'})], ])

#Universe.agents.manage(, kls=Node, kls_kargs=
#Universe.agents.load()
x = '{shell} "{prog} {file}"'.format(shell=Universe.system_shell,
                                       file=__file__, prog=Universe.command_line_prog)
api.clone(x)
#Universe.play()
