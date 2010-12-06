""" cortex.services.postoffice

      a simple service that exposes a message bus.

      TODO: (for json, pickles) annotate messages with data necessary to decode them?

"""

import simplejson

from cortex.core.util import report
from cortex.core.data import EVENT_T, ERROR_T
from cortex.store.ground import Keyspace
from cortex.services import Service
from cortex.core.bus import SelfHostingTupleBus
from cortex.util.decorators import constraint

class PostOffice(Service, Keyspace, SelfHostingTupleBus):
    """ PostOffice Service:

          A wrapper over cyrusbus's basic layout that uses a
          key-value api to access the tuple-space described in
          cortex.store.ground.

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
        keyspace_name  = default_name
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name,
                          parent_space=kargs['universe'].ground )
        SelfHostingTupleBus.__init__(self) # will call self.reset()

    def publish_json(self, label, data):
        """ publish as json """
        self.publish(label, simplejson.dumps(data))

    def publish_pickle(self, label, data):
        """ publish as pickle """
        self.publish(label, pickle.dumps(data))

    def error(self, msg):
        """ shortcut for publishing errors """
        self.publish(ERROR_T, msg)

    def notice(self, msg):
        """ shortcut for publishing errors """
        self.publish(ERROR_T, msg)

    def event(self, msg):
        """ shortcut for publishing events """
        return self.publish(EVENT_T, msg)

    def msg(self, *args, **kargs):
        """ determine caller function and dispatch to publish """
        caller = whosdaddy()
        self.publish(caller['name'],(args, kargs))

    @constraint(boot_first='linda')
    def start(self):
        """ """
        super(Service, self).start()
        self.reset()

class ParanoidPostOffice(PostOffice):
    """ ParanoidPostOffice Service
          Same as PostOffice, but with more restricted access to
          the <publish> operation.
    """

    do_not_discover = True

    def start(self):
        raise Exception,NIY
