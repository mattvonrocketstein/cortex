from cortex.services.gui.parent import Window
class Shell(Window):
    def start(self):
        window = self.spawn_window
        window.add(self.set_shell())
        window.show()
        self.set_prompt()
