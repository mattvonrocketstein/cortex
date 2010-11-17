""" cortex.core.mixins
"""
import os

NOTICE_T = 'system_notice'

class OSMixin(object):
    """ For things that really should be in the os module """

    _procs    = []

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
            exists on the system """
        return 0 == os.system('command -v '+cmd)

    @property
    def ip(self):
        """ """
        pass

    @property
    def hostname(self):
        """ TODO: memoize """
        import socket
        return socket.gethostname()

""" OBSOLETE?

class EventMixin(object):
    def push_events(self, string_type, *args):

        return [self.push_event(string_type, arg) for arg in args]

    def push_event(self, type_string, notice):

        return self.ground.add( (type_string, notice) )

    def events(self,string_type):
        out = self.ground.get_many( (string_type, object) )
        out = [x[1:] for x in out] # clean up by chopping off the token
        return out

class NoticeMixin(EventMixin):

    def push_notice(self, notice):
        return self.push_event(NOTICE_T, notice)

    @property
    def notices(self):
        return self.events(NOTICE_T)
"""

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
