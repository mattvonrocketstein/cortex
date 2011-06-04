""" cortex/services/gui/channel_window.py
"""

import pprint,StringIO

from parent import GUIChild
from console_view import ConsoleView

# standard unpacking method: special name "args" and everything but "args"
unpack = lambda data: ( data['args'],
                        dict([ [d,data[d]] for d in data if d!='args']) )

class ChannelAgent(GUIChild):
    def subscribe(self):
        """ subscribe to the first channel """
        exchange = (self.universe|'postoffice')
        exchange.event.subscribe(self.callback)

    def callback(self, ctx, **data):
        """ called whenever "event" channel is
            subscribed to, outputs it to gtk
            buffer
        """
        self.buffer.write("Sender: " + str(ctx)+'\n')
        args, kargs = unpack(data)

        def doit(v):
            """prepare value for pprint to buffer"""
            x = StringIO.StringIO()
            pprint.pprint(v, x)
            x.seek(0)
            x = x.read()
            x=x.split('\n',) #'\n    ')
            x = [' '*4 + y for y in x]
            x = ''.join(x)+'\n'
            return x
        rendered_args = doit(args)
        rendered_kargs = doit(kargs)
        if args:
            self.buffer.write(rendered_args)
        if kargs:
            self.buffer.write(rendered_kargs)

    def start(self):
        window = self.spawn_window
        S = self.scrolled_window
        x = ConsoleView()
        x.show()
        S.add(x); S.show()
        window.add(S); window.show()
        self.buffer = x  # you can call .write('str') on this thing
        self.subscribe()
