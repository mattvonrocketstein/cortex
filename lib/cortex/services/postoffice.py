""" cortex.services.postoffice

      a simple service that exposes a message bus.

      TODO: (for json, pickles) annotate messages with data necessary to decode them?

"""

import simplejson

from cortex.core.util import report
from cortex.core.data import EVENT_T, ERROR_T
from cortex.core.ground import Keyspace
from cortex.services import Service
from cortex.core.bus import SelfHostingTupleBus
from cortex.core.channels import channel, ChannelManager


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

    ## Begin channel declarations        ( TODO: make this more like promela )
    notice = channel.NOTICE              # shortcut for publishing notices (unused)
    error  = getattr(channel, ERROR_T)   # shortcut for publishing errors  (unused)
    event  = getattr(channel, EVENT_T)   # shortcut for publishing events  (used by term)

    def __init__(self, *args, **kargs):
        """ """
        super(PostOffice,self).__init__( *args, **kargs)
        #Service.__init__(self, *args, **kargs)
        default_name   = 'PostOffice::{_id}::keyspace'.format(_id=str(id(self)))
        keyspace_name  = self.universe or default_name
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name)
        SelfHostingTupleBus.__init__(self) # will call self.reset()

        # sets ``self`` as postoffice for each declared channel
        self.bind_embedded_channels()

    def publish_json(self, label, data):
        """ publish as json """
        self.publish(label, simplejson.dumps(data))

    def publish_pickle(self, label, data):
        """ publish as pickle """
        self.publish(label, pickle.dumps(data))

    def msg(self, *args, **kargs):
        """ push a caller labeled message on to the stack.
            determines caller function and dispatches to publish """
        caller = whosdaddy()
        self.publish(caller['name'], (args, kargs))

    def start(self):
        """ """
        super(PostOffice, self).start()
        self.reset()
