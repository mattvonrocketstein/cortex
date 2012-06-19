""" cortex.services.dojo

    TODO: milestone.. how best to externalize this
"""
import os

from cortex.core.agent import Agent
from cortex.core.util import report
from cortex.services import FecundService
from cortex.agents.proc import Process
from cortex.agents.qmon import QueueMon

class Pile(Agent):
    """ pile of stuff """
    @property
    def storage_dir(self):
        return os.path.join(self.universe.tmpdir, 'dojo_pile')

    def start(self):
        super(Agent,self).start()
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)

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
