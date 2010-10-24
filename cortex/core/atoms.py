""" cortex.core.atoms
"""

class AutonomyMixin:
    def play(self):
        """ """

    def resume(self):
        """ """

    def pause(self):
        """ """

    def freeze(self):
        """ """

    def boot(self):
        """ """
        if self.is_local:
            Universe.launch_instance(self)
        else:
            raise NodeError,"Only node-local's can be booted at this time."

class PerspectiveMixin:
    def darkly(self):
        """ if this host refers to a local version, obtain an image of
            self suitable for acurate transmission/storage elsewhere
        """
        NIY

