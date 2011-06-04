""" cortex.services.terminal._gtk
"""
import gtk
from cortex.services import Service
from cortex.core.data import EVENT_T
from cortex.core.agent import Agent
from cortex.core.util import report, console
from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint

import gtk
from ipython_view import *
import pango
from console_view import ConsoleView

class CommonInterface:
    def set_prompt(self):
        """ ugh copied from ATerminal"""
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.outputcache.prompt2.p_template = console.red(self.universe.name)  + ' [\\#] '

    def handle_control_d(self):
        self.universe.stop()

    def on_key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        #report("Key %s (%d) was pressed" % (keyname, event.keyval))
        if str(keyname)=='Return':
            report("Pressed return")
        if event.state & gtk.gdk.CONTROL_MASK:
          report("Control was being held down")
          if str(keyname)=='Return':
              report("spawning a new gtk-ipython session")
              self.spawn_shell()
          if str(keyname)=='d':
              self.handle_control_d()
        if event.state & gtk.gdk.MOD1_MASK:
            report("Alt was being held down")
        if event.state & gtk.gdk.SHIFT_MASK:
            report("Shift was being held down")

    @property
    def spawn_window(self):
        window = gtk.Window()
        window.set_size_request(750,550)
        window.set_resizable(True)
        window.connect('key_press_event', self.on_key_press)
        window.connect('delete_event',lambda x,y:False)
        window.connect('destroy',lambda x:gtk.main_quit())
        return window

    @property
    def scrolled_window(self):
        S = gtk.ScrolledWindow()
        S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        return S
from cortex.services.terminal import abstract
class GUI(CommonInterface):
    """ """
    def set_shell(self):
        S = self.scrolled_window
        from cortex.core.data import IPY_ARGS
        self.shell = IPythonView(argv=IPY_ARGS,
                        user_ns=abstract.ATerminal .compute_terminal_namespace())

        self.shell.show()
        S.add(self.shell)
        S.show()
        return S

    def really_start(self):
        """ TODO: defer to universe.command_line_options
                  for whether to magic_pdb """
        if not self.universe.config.gtk_reactor==True:
            err  = "This universe isn't configured for GTK reactor, "
            err += "but you're trying to use the gtk terminal!"
            ctx  = str(self)
            self.fault(err, ctx)
            self.universe.stop()

        components  = [ self.spawn_channel_watcher,
                        self.spawn_shell, ]

        for c in components:
            c()
        self.load()

    def spawn_channel_watcher(self):
        report('spawnc')
        self.manage(kls=ChannelAgent, kls_kargs=dict(universe=self.universe),
                    name='ChannelAgent')

    def spawn_shell(self):
        """ interesting.. safe to call multiple times"""
        report('spawns')
        self.manage(kls=Shell, kls_kargs=dict(universe=self.universe), name='ShellAgent')

class GUIChild(Agent, GUI):
    pass

import pprint,StringIO
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

        #self.buffer.write(str(x))
#report(x.read(),stream=self.buffer)


    def start(self):
        window = self.spawn_window
        S = self.scrolled_window
        x = ConsoleView()
        x.show()
        S.add(x); S.show()
        window.add(S); window.show()
        self.buffer = x  # you can call .write('str') on this thing
        self.subscribe()

class Shell(GUIChild):
    def start(self):
        window = self.spawn_window
        window.add(self.set_shell())
        window.show()
        self.set_prompt()


if __name__=='__main__':
    from twisted.internet import reactor
    GUI().start()
    reactor.run( )
