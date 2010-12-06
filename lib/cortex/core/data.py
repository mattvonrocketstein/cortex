""" cortex.core.data
"""

# These functions are so simple they're practically data..
from cortex.core.functional import NOOP, IDENTITY

# pseudo-types for message-passing.. mainly used in conjunction with postoffice
################################################################################
NOT_FOUND_T = "randomjunk NOT_FOUND_T randomjunk"
NOTICE_T = "NOTICE_T"
EVENT_T  = "EVENT_T"
PEER_T   = "PEER_T"
WARN_T   = "WARN_T"
ERROR_T  = "ERROR_T"

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
IPY_ARGS          = ['-noconfirm_exit']

# cortex.services.contrib
################################################################################
AVAHI_TYPE = "_http._tcp" # used in the old (avahi/dbus) peer-discovery strategy
