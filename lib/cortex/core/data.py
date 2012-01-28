""" cortex.core.data
"""

def NOOP(*args, **kargs): pass
def IDENTITY(*args, **kargs):
    """ """
    if args and kargs:
        return args, kargs
    return args or kargs

# pseudo-types for message-passing.. mainly used in conjunction with postoffice
################################################################################
NOTICE_T            = "NOTICE_T"
EVENT_T             = "EVENT_T"
PEER_T              = "PEER_T"
WARN_T              = "WARN_T"
ERROR_T             = "ERROR_T"
CORTEX_API_UPDATE_T = 'cortex_api'

# reflections on cortex codebase
################################################################################
SERVICES_DOTPATH = 'cortex.services'

# generic networking constants
################################################################################
API_PORT          = 1337
CORTEX_PORT_RANGE = (1337, 1473)
GENERIC_LOCALHOST = "0"
LOOPBACK_HOST     = '127.0.0.1'
DEFAULT_HOST      = LOOPBACK_HOST

# cortex.services.terminal
################################################################################
IPY_ARGS          = ['-noconfirm_exit', '-rcfile=~/.ipython/msh.rc']

# cortex.services.contrib
################################################################################
AVAHI_TYPE = "_http._tcp" # used in the old (avahi/dbus) peer-discovery strategy

class _session(object):
    """ """
    def __init__(self):
        self.interactive=False
        self.iset = []

    @property
    def instructions(self):
        return self.iset

    def add_instruction(self,x):
        assert len(x)==3, str(x)
        self.iset.append(x)
    def filter_by_name(self,n):
        return [x for x in self.iset if x[0]!=n]

    def set_interactive(self,v=True):
        """ """
        self._interactive = v
        term_args   = {}                                     # Cortex-Terminal arguments
        terminal_instruction = [ "load_service", ("terminal",),       term_args  ]
        if v and terminal_instruction not in self.iset:
            self.iset.append(terminal_instruction)
        else:
            try:
                self.iset.remove(terminal_instruction)
            except ValueError:
                pass

class _standardsession(_session):
    def __init__(self):
        super(_standardsession,self).__init__()
        self.add_instruction([ "load_service", ("_linda",), {} ])
        self.add_instruction([ "load_service", ("postoffice",), {} ])
