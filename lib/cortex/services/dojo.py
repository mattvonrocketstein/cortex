""" cortex.services.dojo

    TODO: milestone.. how best to externalize this
"""

from cortex.services import FecundService
from cortex.agents.proc import Process
from cortex.core.agent import Agent
from cortex.core.util import report
from cortex.mixins.flavors import LoopingCall

class DojoProcess(Process):
    _cmd = './node/bin/dojo --conf ~/code/robotninja/dojo.ini'
    #_cmd = 'python -c"for x in range(10): print x" '

class QueueMon(Agent):
    max_size = 200

    def setup(self):
        olditerate = self.iterate
        lc = LoopingCall(olditerate)
        def newiterate(): lc.start(5)
        self.iterate = newiterate

    def clean_queue(self, q, name="anonymous"):
        """ clean_queue simply downsizes a queue by
            throwing away the entries if qsize > max_size
        """
        if q.qsize() > self.max_size:
            report("cleaning queue",name)
            while q.qsize() > self.max_size:
                q.get()

    def iterate(self):
        """ self.queues should return be thing like a dict, a
            dict.items(), or a flat list.
        """
        qs = self.queues
        if qs:
            if isinstance(qs, dict):
                qs = qs.items()
            elif all([isinstance(qs, (list,tuple)),
                      not isinstance(qs[0],(list, tuple))]):
                qs = [['anonymous',q] for q in qs]
        else:
            report('"queues" is empty or false?')
            return
        for name,q in qs:
            self.clean_queue(q, name)

class Janitor(QueueMon):
    """ make sure that the queue in DojoProcess
        tracking stdout doesn't get too large.
    """
    max_size = 200

    @property
    def queues(self):
        djp = self.siblings['DojoProcess']
        stdout = djp._stdout
        stderr = djp._stderr
        return dict(stdout=stdout, stderr=stderr)

class Dojo(FecundService):

    class Meta:
        children = [ DojoProcess, Janitor ]
