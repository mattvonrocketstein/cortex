""" cortex.services.gui.common
"""
import gtk
from cortex.core.util import report

console = report.console

class CommonInterface:

    def set_prompt(self):
        """ ugh copied from ATerminal"""
        self.shell.IP.outputcache.prompt1.p_template = console.blue(self.universe.name) + ' [\\#] '
        self.shell.IP.outputcache.prompt2.p_template = console.red(self.universe.name)  + ' [\\#] '

    def handle_control_d(self):
        """ """
        self.universe.stop()

    def clear_screen(self):
        self.shell.get_buffer().set_text('')
        self.shell._processLine()

    handle_control_l = clear_screen

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
          handler = getattr(self,'handle_control_' + keyname, None)
          if handler: handler()

        if event.state & gtk.gdk.MOD1_MASK:
            report("Alt was being held down")
        if event.state & gtk.gdk.SHIFT_MASK:
            report("Shift was being held down")

    @property
    def spawn_window(self):
        window = gtk.Window()
        #gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(750,550)
        window.set_resizable(True)
        window.set_title("cortex")
        window.connect('key_press_event', self.on_key_press)
        window.connect('delete_event',lambda x,y:False)
        window.connect('destroy',lambda x:gtk.main_quit())
        return window

    @property
    def menu(self):
        # Init the menu-widget, and remember -- never
        # show() the menu widget!!
        # This is the menu that holds the menu items, the one that
        # will pop up when you click on the "Root Menu" in the app
        menu = gtk.Menu()

        # Next we make a little loop that makes three menu-entries for
        # "test-menu".  Notice the call to gtk_menu_append.  Here we are
        # adding a list of menu items to our menu.  Normally, we'd also
        # catch the "clicked" signal on each of the menu items and setup a
        # callback for it, but it's omitted here to save space.
        for i in range(3):
            # Copy the names to the buf.
            buf = "Test-undermenu - %d" % i

            # Create a new menu-item with a name...
            menu_items = gtk.MenuItem(buf)

            # ...and add it to the menu.
            menu.append(menu_items)

            # Do something interesting when the menuitem is selected
            #menu_items.connect("activate", self.menuitem_response, buf)

            # Show the widget
            menu_items.show()

        # This is the root menu, and will be the label
        # displayed on the menu bar.  There won't be a signal handler attached,
        # as it only pops up the rest of the menu when pressed.
        root_menu = gtk.MenuItem(self.name)

        root_menu.show()
        # Now we specify that we want our newly created "menu" to be the
        # menu for the "root menu"
        root_menu.set_submenu(menu)


        # Create a menu-bar to hold the menus and add it to our main window
        menu_bar = gtk.MenuBar()
        #vbox.pack_start(menu_bar, False, False, 2)
        menu_bar.show()

        # And finally we append the menu-item to the menu-bar
        menu_bar.append(root_menu)
        return menu_bar

    @property
    def vbox(self):
        # A vbox to put a menu and a button in:
        vbox = gtk.VBox(False, 0)
        #vbox.pack_start(self.menu, gtk.FALSE, gtk.FALSE, 2)
        #window.add(vbox)
        vbox.show()
        return vbox


    @property
    def scrolled_window(self):
        S = gtk.ScrolledWindow()
        S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        return S
