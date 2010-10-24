""" cortex.core.node
"""

import os

from cortex.core.common import NodeError
from cortex.core.data import LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin

class Node(object, AutonomyMixin, PerspectiveMixin):
    """
    """

    def __init__(self, host=None, instance=None, resource_description=None):
        """
        """
        self.host = host
        self.instance = instance
        self.resource_description = resource_description

    def __render_resource_description(self): return str(self.resource_description)

    def __str__(self):
        host = str(self.host)
        instance = str(self.instance)
        resource_descr = self.__render_resource_description()
        return "<Node@" + host + "::" + instance + " " + resource_descr + ">"

    @property
    def is_local(self):
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]
