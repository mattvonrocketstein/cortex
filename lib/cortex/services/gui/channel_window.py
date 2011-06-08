""" cortex/services/gui/channel_window.py
"""
import gtk
import pprint,StringIO

from cortex.core.data import EVENT_T
from parent import GUIChild
from console_view import ConsoleView
from cortex.core.channels import unpack, declare_callback

def prepare(v):
    """prepare value for pprint to buffer"""
    x = StringIO.StringIO()
    pprint.pprint(v, x)
    x.seek(0)
    x = x.read()
    x=x.split('\n',)
    #x = [' '*4 + y for y in x]
    x = [' ' + y for y in x]
    x = ''.join(x)+'\n'
    return x

def handler_factory(CHAN):
    @declare_callback(channel=CHAN)
    def event_handler(self, ctx, **data):
        """ called whenever "exchange" channel is
            subscribed to, outputs it to gtk
            buffer. see channels.py for a
            description of conventions involving
            the usage of ctx / data
        """
        def write_ctx(ctx):
            'write context/path'
            #unpack_ctx(ctx)
            self.buffer.write("Sender: " + str(ctx)+'\n')

        def write_data(data):
            "write args, kargs"
            args, kargs = unpack(data)
            if args:
                rendered_args = prepare(args)
                self.buffer.write(rendered_args)
            if kargs:
                rendered_kargs = prepare(kargs)
                self.buffer.write(rendered_kargs)

        write_ctx(ctx)
        write_data(data)
    return event_handler

class ChannelAgent(GUIChild):
    """ """
    def start(self):
        """ agent protocol """
        super(ChannelAgent,self).start()
        window = self.spawn_window
        vbox = self.vbox
        S = self.scrolled_window
        x = ConsoleView(); x.show()
        S.add(x); S.show()
        vbox.pack_start(self.menu, gtk.FALSE, gtk.FALSE, 2)
        vbox.pack_end(S, True, True, 2); vbox.show()
        window.add(vbox); window.show()
        #window.add(S); window.show()
        self.buffer = x  # you can call .write('str') on this thing

def channel_agent_factory(CHAN):
    return type('AnonymousChannelAgent',
                (ChannelAgent,),
                dict(event_handler=handler_factory(CHAN)))
