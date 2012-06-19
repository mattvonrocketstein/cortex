""" cortex.agents.process
"""
import re, shlex
import twisted
from StringIO import StringIO
from Queue import Queue, Empty
from twisted.internet import protocol

from cortex.core.util import report
from cortex.core.agent import Agent

def q2txt(q):
    """ """
    out = StringIO()
    while True:
        try:
            data = q.get(block=False)
            report(data)
            out.write(data)
        except Empty:
            break
    out.flush()
    out.seek(0)
    return out.read()

class Process(Agent, protocol.ProcessProtocol):
    """
        TODO: shutdown the process less brutally when cortex terminates
    """

    def connectionMade(self):
        """ """
        self.transport.closeStdin()

    def outReceived(self, data):
        """ """ #report( "outReceived! with %d bytes!" % len(data))
        self._stdout.put(data)

    def errReceived(self, data):
        """ """ #report( "errReceived! with %d bytes!" % len(data))
        self._stderr.put(data)

    def inConnectionLost(self):
        """ """
        pass #report( "inConnectionLost! stdin is closed! (we probably did it)")

    def outConnectionLost(self):
        """ """
        report("outConnectionLost! The child closed their stdout! queue-length: ",
               self._stdout.qsize())

    def errConnectionLost(self):
        """ """
        report('errConnectionLost! The child closed their stderr. queue-length: ',
               self._stderr.qsize())

    def processExited(self, reason):
        """ """
        self.finish(reason)

    def finish(self, reason):
        """ """
        err = reason.value.exitCode
        report( "processExited, status", err)
        if err:
            txt = q2txt(self._stderr)
            report(txt)

    def processEnded(self, reason): self.finish(reason)

    @property
    def stdout(self):
        """ exhausts the queue """
        return q2txt(self._stdout)

    @property
    def stderr(self):
        """ exhausts the queue """
        return q2txt(self._stderr)

    def _kill(self):
        """ This will eventually result in processEnded being called. """
        self.transport.signalProcess('KILL')

    def stop(self):
        """ """
        report('Killing process: ', self._cmd)
        try:
            self._kill()
        except twisted.internet.error.ProcessExitedAlready:
            pass
        super(Process, self).stop()

    def setup(self):
        """ """
        self._stdout = Queue()
        self._stderr = Queue()
        self.count   = 0
        self.process = None

    @property
    def cmd(self):
        """ """
        cmd = self._cmd
        cmd = shlex.split(cmd)
        args = cmd[1:] or [''] # doesn't like "null argv"? wtf
        executable = cmd[0]
        return executable, args

    def iterate(self):
        """ """
        env = {}
        executable, args = self.cmd
        sp_args = (self, executable, args, env)
        self.process = self.universe.reactor.spawnProcess(*sp_args)

    def start(self):
        """ """
        super(Process, self).start()
        restart_statuses = [ -1, # not started
                             9, # recently killed
                             ]
        if getattr(self.process, 'status', None) in restart_statuses:
            # can't do this without a check because play() uses iterate upstream
            self.iterate()
