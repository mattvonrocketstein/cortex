""" cortex.services.dojo

    TODO: milestone.. how best to externalize this
"""

from cortex.core.agent import Agent
from cortex.core.util import report
from cortex.services import FecundService
from cortex.agents.proc import Process
from cortex.agents.qmon import QueueMon

class Pile(Agent):
    """ pile of stuff """
    def iterate(self):
        report('pile here')

class DojoProcess(Process):
    _cmd = './node/bin/dojo --conf ~/code/robotninja/dojo.ini'

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
        children = [ DojoProcess, Janitor, Pile ]
