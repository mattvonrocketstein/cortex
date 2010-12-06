""" cortex.core.clone

      A clone is basically a non-local universe, and so
      should eventually obey most of the universe's api.

      Example usage follows:

          Universe(28489)[master:1338]@telemachus [6] universe.clones
          Out[6]: CloneManager(['slave-a2e11c14-00e1'])

          Universe(28489)[master:1338]@telemachus [7] universe.clones[0].pids
          Out[7]: [28497, 28498]
          Universe(28489)[master:1338]@telemachus [8] universe.clones[0].kill()

           (clone window disppears)
"""

from cortex.core.manager import Manager
from cortex.core.hds import HDS

class Clone(HDS):
    """ """
    def __repr__(self):
        return self.label

    @property
    def pids(self):
        """ HACK """
        from cortex.core.universe import Universe
        return Universe.pids_for_pattern(self.label)

    def kill(self):
        from cortex.core.universe import Universe
        raise Exception,"Refusing to kill a clone with no label"
        return [p.kill() for p in Universe.procs_for_pattern(self.label)]


class CloneManager(Manager):
    """
         asset_class:= Class specifying how the objects in this
                       container will be represented
    """
    asset_class=Clone

CLONES = CloneManager()
