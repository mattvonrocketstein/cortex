""" cortex.agents.process
"""
import re, shlex
import twisted
from StringIO import StringIO
from Queue import Queue, Empty
from twisted.internet import protocol

from cortex.core.util import report
from cortex.core.agent import Agent

class MyPP(protocol.ProcessProtocol):
    def __init__(self, verses=10):
        self.stdout = Queue()
        self.stderr = Queue()
        self.verses = verses

        self.count = 0

    def connectionMade(self):
        #report( "connectionMade!")
        self.transport.closeStdin() # tell them we're done

    def outReceived(self, data):
        #report( "outReceived! with %d bytes!" % len(data))
        self.stdout.put(data)

    def errReceived(self, data):
        #report( "errReceived! with %d bytes!" % len(data))
        self.stderr.put(data)

    def inConnectionLost(self):
        pass #report( "inConnectionLost! stdin is closed! (we probably did it)")

    def outConnectionLost(self):
        report("outConnectionLost! The child closed their stdout! queue-length: ",
               self.stdout.qsize())

    def errConnectionLost(self):
        report('errConnectionLost! The child closed their stderr. queue-length: ',
               self.stderr.qsize())

    def processExited(self, reason): self.finish(reason)

    def finish(self, reason):
        err = reason.value.exitCode
        report( "processExited, status", err)
        if err:
            txt = q2txt(self._stderr)
            report(txt)

    def processEnded(self, reason): self.finish(reason)

def  q2txt(q):
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

class Process(Agent):
    """
        TODO: shutdown the process less brutally when cortex terminates
    """

    @property
    def _stdout(self): return self.pp.stdout

    @property
    def stdout(self):
        """ exhausts the queue"""
        return q2txt(self._stdout)

    @property
    def _stderr(self): return self.pp.stderr

    @property
    def stderr(self):
        """ exhausts the queue"""
        return q2txt(self._stderr)

    def _kill(self):
        """ This will eventually result in processEnded being called. """
        self.pp.transport.signalProcess('KILL')

    def stop(self):
        report('Killing process: ', self._cmd)
        try:
            self._kill()
        except twisted.internet.error.ProcessExitedAlready:
            pass
        super(Process, self).stop()

    @property
    def cmd(self):
        cmd = self._cmd
        cmd = shlex.split(cmd)
        args = cmd[1:] or [''] # doesn't like "null argv"? wtf
        executable = cmd[0]
        return executable, args

    def iterate(self):
        self.pp = MyPP()
        env = {}
        executable, args = self.cmd
        self.process = self.universe.reactor.spawnProcess(self.pp, executable, args, env)
