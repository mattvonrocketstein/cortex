""" cortex.core.mixins
"""
import os

class MobileCodeMixin(object):
    """ """
    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]

class OSMixin(object):
    """ For things that really should be in the os module """

    _procs    = []

    @property
    def isposix(self):
        import sys
        return 'posix' in sys.builtin_module_names
    is_posix = isposix
    posix = is_posix

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
    def ip(self):
        """ """
        pass

    @property
    def hostname(self):
        """
             TODO: memoize """
        import platform
        import socket
        return socket.gethostname()#, platform.node

class PIDMixin:
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
