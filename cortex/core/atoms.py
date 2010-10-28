""" cortex.core.atoms
"""

from cortex.core.util import report

class AutonomyMixin:
    def play(self):
        """ """
        report("play for "+self.name)

    def resume(self):
        """ """
        report("resume for "+self.name)
    def pause(self):
        """ """
        report("pause for "+self.name)
    def freeze(self):
        """ """
        report("freeze for "+self.name)
    def boot(self):
        """ """
        report("boot for "+self.name)
        if self.is_local:
            Universe.launch_instance(self)
        else:
            raise NodeError,"Only node-local's can be booted at this time."

class PerspectiveMixin:
    def darkly(self):
        """ if this host refers to a local version, obtain an image of
            self suitable for acurate transmission/storage elsewhere
        """
        report("darkly for "+self.name)

