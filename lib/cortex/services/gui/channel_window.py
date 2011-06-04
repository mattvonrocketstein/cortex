""" cortex/services/gui/channel_window.py
"""

import pprint,StringIO

from cortex.core.data import EVENT_T
from parent import GUIChild
from console_view import ConsoleView
from cortex.core.channels import unpack, declare_callback

class ChannelAgent(GUIChild):
    """ """
    def __init__(self, *args, **kargs):
        super(ChannelAgent,self).__init__(*args, **kargs)

    @staticmethod
    def prepare(v):
        """prepare value for pprint to buffer"""
        x = StringIO.StringIO()
        pprint.pprint(v, x)
        x.seek(0)
        x = x.read()
        x=x.split('\n',) #'\n    ')
        x = [' '*4 + y for y in x]
        x = ''.join(x)+'\n'
        return x

    @declare_callback(channel=EVENT_T)
    def callback(self, ctx, **data):
        """ called whenever "exchange" channel is
            subscribed to, outputs it to gtk
            buffer
        """
        def write_ctx(ctx):
            'write context/path'
            #unpack_ctx(ctx)
            self.buffer.write("Sender: " + str(ctx)+'\n')

        def write_data(data):
            "write args, kargs"
            args, kargs = unpack(data)
            if args:
                rendered_args = self.prepare(args)
                self.buffer.write(rendered_args)
            if kargs:
                rendered_kargs = self.prepare(kargs)
                self.buffer.write(rendered_kargs)

        write_ctx(ctx)
        write_data(data)

    def start(self):
        """ agent protocol """
        super(ChannelAgent,self).start()
        window = self.spawn_window
        S = self.scrolled_window
        x = ConsoleView()
        x.show()
        S.add(x); S.show()
        window.add(S); window.show()
        self.buffer = x  # you can call .write('str') on this thing
