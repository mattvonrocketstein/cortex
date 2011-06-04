""" cortex.services.gui.common
"""
import gtk
from cortex.core.util import report, console

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
