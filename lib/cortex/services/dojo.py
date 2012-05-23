""" cortex.services.dojo

    TODO: milestone.. how best to externalize this
"""

from cortex.services import FecundService
from cortex.agents.proc import Process
from cortex.core.agent import Agent
from cortex.core.util import report
from cortex.mixins.flavors import LoopingCall

class DojoProcess(Process):
    #_cmd = './node/bin/dojo --conf ~/code/robotninja/dojo.ini'
    _cmd = 'yes dammit'

class Janitor(Agent):
    """ make sure that the queue in DojoProcess
        tracking stdout doesn't get too large.
    """

    max_size = 200

    def setup(self):
        olditerate = self.iterate
        lc = LoopingCall(olditerate)
        def newiterate(): lc.start(5)
        self.iterate = newiterate

    @property
    def queues(self):
        djp = self.siblings['DojoProcess'] # self.parent.children()[0]
        stdout = djp.stdout
        stderr = djp.stderr
        return stdout, stderr

    def iterate(self):
        stdout,stderr = self.queues
        def clean(q,name):
            if q.qsize() > self.max_size:
                report("cleaning queue",name)
                while q.qsize() > self.max_size:
                    q.get()
        clean(stdout, 'stdout')
        clean(stderr, 'stderr')


class Dojo(FecundService):

    class Meta:
        children = [ DojoProcess, Janitor ]
