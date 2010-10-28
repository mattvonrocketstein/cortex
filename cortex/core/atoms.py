""" cortex.core.atoms
"""

class AutonomyMixin:
    def play(self):
        """ """
        print "play for "+self.name
    def resume(self):
        """ """
        print "resume for "+self.name
    def pause(self):
        """ """
        print "pause for "+self.name
    def freeze(self):
        """ """
        print "freeze for "+self.name
    def boot(self):
        """ """
        print "boot for "+self.name
        if self.is_local:
            Universe.launch_instance(self)
        else:
            raise NodeError,"Only node-local's can be booted at this time."

class PerspectiveMixin:
    def darkly(self):
        """ if this host refers to a local version, obtain an image of
            self suitable for acurate transmission/storage elsewhere
        """
        print "darkly for "+self.name

