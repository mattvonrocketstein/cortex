""" cortex.services.terminal._gtk
"""
import gtk
from cortex.services import Service
from cortex.core.data import EVENT_T
from cortex.core.util import report, console
from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint

import gtk
from ipython_view import *
import pango
from console_view import ConsoleView

class GUI_GTK:
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

class GUI(GUI_GTK):
    """ """

    def set_channel(self):
        S = self.scrolled_window
        x = ConsoleView()
        x.show()
        S.add(x)
        S.show()
        return S,x

    def set_shell(self):
        S = self.scrolled_window
        from cortex.core.data import IPY_ARGS
        self.shell = IPythonView(argv=IPY_ARGS,
                        user_ns=self.compute_terminal_namespace())

        self.shell.show()
        S.add(self.shell)
        S.show()
        return S





    def really_start(self):
        """ TODO: defer to universe.command_line_options for whether to magic_pdb """
        if not self.universe.config.gtk_reactor==True:
            err = "This universe isn't configured for GTK reactor, but you're trying to use the gtk terminal"
            ctx = 'test'
            self.fault(err, ctx)
            self.universe.stop()

        components  = [self.spawn_channel_watcher
                       ,self.spawn_shell,]


        for c in components:
            c()

    def spawn_channel_watcher(self):
        window = self.spawn_window
        x,y = self.set_channel()
        window.add(x)
        window.show()
        return y

    def spawn_shell(self):
        """ interesting.. safe to call multiple times"""
        window = self.spawn_window
        window.add(self.set_shell())
        window.show()
        self.set_prompt()

if __name__=='__main__':
    from twisted.internet import reactor
    GUI().start()
    reactor.run( )
