""" cortex.services.gui.shell

    since there's not much here it might seem fragmented to have
    an agent for this rather than just putting this in the GUI
    service directly, but it makes sense if you think about the
    possibility of the gui having menus, and split panes, and
    scrolling log buffers, etc etc

"""
from cortex.services.gui.parent import Window
class Shell(Window):
    def start(self):
        window = self.spawn_window
        window.add(self.set_shell())
        window.show()
        self.set_prompt()
