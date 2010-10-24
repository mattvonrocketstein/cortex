""" cortex.core.universe
"""

from cortex.core.atoms import AutonomyMixin, PerspectiveMixin

class __Universe__(object, AutonomyMixin, PerspectiveMixin):
    """
        NOTE: this should effectively be a singleton
    """

    class shell:
        def __init__(self, path):
            self.path = path

        def __call__(self, line, quiet=False):
            os.system('cd "'+path+'"; '+line)

    def launch_instance(self, **kargs):
        from cortex.core.node import Node
        print Node(**kargs)
        #path = node.path
        #shell = self.shell(inside=path)
        #shell("./go")

Universe = __Universe__()
