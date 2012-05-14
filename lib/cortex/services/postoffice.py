""" cortex.services.postoffice

      a service that exposes a message bus.

      # get a list of subscribers by name
      >>> postoffice['EVENT_T']
      (<bound method Terminal.push_q of <Terminal-Service 176000620>>,)

      # get a specific channel object
      >>> events = postoffice.event
      >>> events
      <CHAN-(EVENT_T)>

"""

import simplejson

from cortex.core.util import report
from cortex.core.data import EVENT_T, ERROR_T, PEER_T
from cortex.core.ground import Keyspace
from cortex.services import Service
from cortex.core.bus import SelfHostingTupleBus
from channel import channel, ChannelManager


class PostOffice(Service, Keyspace, SelfHostingTupleBus, ChannelManager):
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

    ## Begin embedded channel declarations  ( TODO: make this more like promela )
    notice = channel.NOTICE                 # shortcut for publishing notices (unused)
    error  = getattr(channel, ERROR_T)      # shortcut for publishing errors  (unused)
    event  = getattr(channel, EVENT_T)      # shortcut for publishing events  (used by term)
    peers  = getattr(channel, PEER_T)

    def __init__(self, *args, **kargs):
        """ PostOffice.__init__
        """
        # initialize keyspace and embedded channels
        default_name   = 'PostOffice::{_id}::keyspace'.format(_id=str(id(self)))
        keyspace_name  = self.universe or default_name
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name)
        self.bind_embedded_channels()

        # will call self.reset()
        SelfHostingTupleBus.__init__(self)

        # calling super() here seems correct but is not.. 'name' will be set incorrectly
        Service.__init__(self, *args, **kargs)

    def publish_json(self, label, data):
        """ publish as json """
        self.publish(label, simplejson.dumps(data))

    def msg(self, *args, **kargs):
        """ pushes a caller-labeled message on to the stack.
            determines caller function and dispatches to publish """
        caller = whosdaddy()
        self.publish(caller['name'], (args, kargs))

    def start(self):
        """ """
        super(PostOffice, self).start()
        self.reset()
