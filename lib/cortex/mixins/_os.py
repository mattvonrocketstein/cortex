""" cortex.mixins._os
"""

import socket
import os, sys
import tempfile
import platform

from goulash.net import ipaddr_hosts
from goulash.net import ipaddr_basic

from cortex.core.util import report


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

    def kill_pid(self, p):
        """ kill a process tree under PID p

            TODO: use psutil.
        """
        if p:
            report('killing pid:', p)
            os.system('kill -KILL {0}'.format(p))

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
    def command_line_prog(self):
        return self.command_line_invocation.split()[0]

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
        return ipaddr_basic()

    @property
    def hosts(self):
        x = ipaddr_hosts()
        return x[1]+[x[0]]

    @property
    def hostname(self):
        return socket.gethostname()#, platform.node
    host = hostname

    @property
    def tmpdir(self):
        """ tempfile.gettempdir() would return /tmp,
            but we prefer to use something relative to
            sys.prefix in case this is an environment
            constructed with 'virtualenv'.
        """
        tmpdir = os.path.join(sys.prefix, 'tmp')
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        return tmpdir

    def tmpfname(self, suffix=''):
        """ suggest a name for temporary file.
            if suffix is provided it will be treated
            as a file extension
        """
        tmpdir = self.tmpdir
        if suffix and not suffix.startswith('.'): suffix='.'+suffix
        return tempfile.mktemp(suffix=suffix, dir=tmpdir)

    def tmpfile(self):
        """ return an open file object pointing at a new temporary file """
        tmpdir = self.tmpdir
        return tempfile.NamedTemporaryFile(delete=False, dir=tmpdir)
