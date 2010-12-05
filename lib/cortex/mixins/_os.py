""" cortex.mixins._os
"""

import os, sys, platform
from cortex.core.util import report
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE

import psutil

class PIDMixin(object):
    """ os pid properties """

    def kill_pids(self, pids):
        """ HACK """
        if not pids: return
        line="kill -KILL {pid_list}".format(pid_list=' '.join([str(pid) for pid in pids]))
        print "running line"
        print "  "+line

        os.system(line)

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

    def procs_for_pattern(self, pattern):
        return [ p for p in psutil.get_process_list() if any([pattern in x for x in p.cmdline])]

    def pids_for_pattern(self, pattern):
        return [ p.pid for p in self.procs_for_pattern(pattern) ]

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

    @property
    def tmpdir(self):
        """ """
        #assert is_cortex_venv(sys.prefix), 'Expected sys.prefix would be a cortex venv'
        tmpdir = os.path.join(sys.prefix, 'tmp')
        if not os.path.exists(tmpdir):
            report('making temporary directory:',tmpdir)
            os.mkdir(tmpdir)
        return tmpdir

    def tmpfile(self):
        """ return a new temporary file """
        tmpdir = self.tmpdir
        return NamedTemporaryFile(delete=False, dir=tmpdir)
