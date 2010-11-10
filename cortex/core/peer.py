""" cortex.core.peer
"""

from cortex.core.node import Node
from cortex.core.manager import Manager

class PeerManager(Manager):
    """ """

    class Peer(object):
        pass

    def __iter__(self):
        """ dumb proxy """
        return Manager.__iter__(self)


