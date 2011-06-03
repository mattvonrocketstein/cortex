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

import platform
if platform.system()=="Windows":
    FONT = "Lucida Console 9"
else:
    FONT = "Luxi Mono 10"

class GUI:
    """ """
    def pre_prompt_hook(self, *args):
        print 'preprompt'
    def set_shell(self):
        #from cortex.services.terminal.terminal import IPShellTwisted, IPY_ARGS
        #self.shell = IPShellTwisted(argv=IPY_ARGS,
        #                            user_ns=self.compute_terminal_namespace(),
        #                            controller=self)
        self.shell.IP.set_hook('pre_prompt_hook', self.pre_prompt_hook)
        #self.shell.IP.BANNER = console.draw_line(display=False)
        # Set IPython "autocall" to "Full"
        #self.shell.IP.magic_autocall(2)
        pass


    def set_prompt(self):
        """
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.outputcache.prompt2.p_template = console.red(self.universe.name)  + ' [\\#] '
        """
        pass

    def handle_control_d(self):
        self.universe.stop()

    def really_start(self):
        """ TODO: defer to universe.command_line_options for whether to magic_pdb """
        if not self.universe.config.gtk_reactor==True:
            err = "This universe isn't configured for GTK reactor, but you're trying to use the gtk terminal"
            ctx = 'test'
            self.fault(err, ctx)
            self.universe.stop()

        W = gtk.Window()
        W.set_size_request(750,550)
        W.set_resizable(True)
        W.connect('key_press_event', self.on_key_press)

        S = gtk.ScrolledWindow()
        S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        from cortex.core.data import IPY_ARGS
        V = IPythonView(argv=IPY_ARGS,
                        user_ns=self.compute_terminal_namespace())
        self.shell = V
        V.modify_font(pango.FontDescription(FONT))
        V.set_wrap_mode(gtk.WRAP_CHAR)
        V.show()
        S.add(V)
        S.show()
        W.add(S)

        W.show()
        W.connect('delete_event',lambda x,y:False)
        W.connect('destroy',lambda x:gtk.main_quit())
        #gtk.main()

    def on_key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        #report("Key %s (%d) was pressed" % (keyname, event.keyval))
        if str(keyname)=='Return':
            report("Pressed return")
        if event.state & gtk.gdk.CONTROL_MASK:
          report("Control was being held down")
          if str(keyname)=='d':
              self.handle_control_d()
        if event.state & gtk.gdk.MOD1_MASK:
            report("Alt was being held down")
        if event.state & gtk.gdk.SHIFT_MASK:
            report("Shift was being held down")

    def before_start(self):
        pass

    def after_start(self):
        self.set_shell()
        self.set_prompt()


if __name__=='__main__':
    from twisted.internet import reactor
    GUI().start()
    reactor.run( )
