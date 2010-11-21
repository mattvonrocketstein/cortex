""" cortex.core.mixins
"""
import os
import sys

class MobileCodeMixin(object):
    """ """
    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]


class PIDMixin(object):
    """ os pid properties """

    @property
    def parent_pid(self):
        """ should be the pid of the bash process
                  of "go" -- the phase 1 init platform
        """
        return os.getppid()

    @property
    def child_pid(self):
        return getattr(self, 'procs', []) and \
               [proc.pid for proc in self.procs]
    child_pids=child_pid

    @property
    def pids(self):
        return dict(parent=self.parent_pid,
                    self=self.pid,
                    children=self.child_pid)

    @property
    def pid(self):
        """ """
        return os.getpid()

class OSMixin(PIDMixin):
    """ For things that really should be in the os module """

    _procs    = []

    @property
    def isposix(self):
        return 'posix' in sys.builtin_module_names
    is_posix = isposix
    posix = is_posix

    @property
    def command_line_invocation(self):
        return ' '.join(sys.argv)

    @property
    def procs(self):
        """ """
        return self._procs

    @property
    def threads(self):
        """ """
        import threading
        return threading.enumerate()

    def has_bin(self, cmd):
        """ use POSIX "command" tool to see if a binary
            exists on the system
            """
        if self.is_posix:
            return os.popen('command -v '+cmd).read().strip()
            #return 0 == os.system('command -v ' + cmd)
        else:
            return NIY
    has_command=has_bin

    @property
    def ips(self):
        """ """
        from cortex.util.net import ipaddr_basic
        return ipaddr_basic()

    @property
    def hosts(self):
        from cortex.util.net import ipaddr_hosts
        x=ipaddr_hosts()
        return x[1]+[x[0]]

    @property
    def hostname(self):
        """
             TODO: memoize """
        import platform
        import socket
        return socket.gethostname()#, platform.node


import Queue
from Queue import Empty as QueueEmpty
class LocalQueue:
    """ """
    def __len__(self):
        return self.event_q.qsize()

    def init_q(self):
        """ """
        self.event_q = Queue.Queue()

    def push_q(self, *args, **kargs):
        """ """
        return self.event_q.put([args, kargs])

    def pop_q(self):
        """ """
        try:
            return self.event_q.get(block=False)
        except QueueEmpty:
            pass
