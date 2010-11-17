""" cortex.services.postoffice

      a simple service that exposes a message bus
"""

from cortex.core.util import report
from cortex.core.ground import Keyspace
from cortex.services import Service

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

        Bus.__init__(self) # will call self.reset()

    def msg(self, *args, **kargs):
        """ TODO: determine caller function and dispatch to publish
        """
        NIY

    def start(self):
        """ """
        super(Service,self).start()
        self.reset()
