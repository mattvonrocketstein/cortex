""" cortex.core.data
"""

# pseudo-types for message-passing.. mainly used in conjunction with postoffice
################################################################################
WARN_T   = "WARN_T"
NOTICE_T = "NOTICE_T"
EVENT_T  = "EVENT_T"
PEER_T   = "PEER_T"

# reflections on cortex codebase
################################################################################
SERVICES_DOTPATH = 'cortex.services'

# generic networking constants
################################################################################
GENERIC_LOCALHOST = "0"
LOOPBACK_HOST     = '127.0.0.1'
DEFAULT_HOST      = LOOPBACK_HOST

# cortex.services.terminal
################################################################################
IPY_ARGS          = ['-noconfirm_exit']

# cortex.services.contrib
################################################################################
AVAHI_TYPE = "_http._tcp" # used in the old (avahi/dbus) peer-discovery strategy
