""" cortex.services.postoffice

      a simple service that exposes a message bus
"""

import simplejson

from cortex.core.util import report
from cortex.core.ground import Keyspace
from cortex.services import Service
from cortex.core.bus import SelfHostingTupleBus

class PostOffice(Service, Keyspace, SelfHostingTupleBus):
    """ PostOffice Service:
          A wrapper over cyrusbus's basic layout that uses a
          key-value api to access the tuple-space described in
          cortex.core.ground.

          start: brief description of service start-up here
          stop:  brief description service shutdown here

        TODO: either wrap TupleBus.publish up in something asynchronous,
              or guarantee that subscriber-callbacks are themselves
              non-blocking.
    """

    def __init__(self, *args, **kargs):
        """ """
        Service.__init__(self, *args, **kargs)
        default_name   = 'PostOffice::{_id}::keyspace'.format(_id=str(id(self)))
        keyspace_name  = self.universe or default_name
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name)
        SelfHostingTupleBus.__init__(self) # will call self.reset()

    def introduce(self, data):
        """ announce peer discovery """
        from cortex.core.data import PEER_T
        self.publish(PEER_T, simplejson.dumps(data))

    def msg(self, *args, **kargs):
        """ TODO: determine caller function and dispatch to publish
        """
        NIY

    def start(self):
        """ """
        super(Service,self).start()
        self.reset()

class ParanoidPostOffice(PostOffice):
    """ ParanoidPostOffice Service
          Same as PostOffice, but with more restricted access to
          the <publish> operation.
    """

    do_not_discover = True

    def start(self):
        raise Exception,NIY
