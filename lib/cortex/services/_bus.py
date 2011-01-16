""" cortex.services._bus
"""

from cyrusbus.bus import Bus

from cortex.core.util import report
from cortex.store.keyspace import Keyspace
from cortex.services import Service


class TupleBus(Bus):
    """ a wrapper over cyrusbus to use tuples
         (by default it uses lists and dictionaries)

        cyrusbus also uses a "subscriptions object",
        which is simply a key/callback dictionary.  this
        version simplifies that by just storing callbacks.
    """

    def unsubscribe(self, key, callback):
        if not self.has_subscription(key, callback):
            return self
        self.subscriptions[key] = tuple([cb for cb in self.subscriptions[key] if cb!=callback])

    def has_subscription(self, key, callback):
        """ override from cyrusbus enforcing simple callbacks as
            subscriptions (by default cyrusbus uses dictionaries)
        """
        if key not in self.keys():
            return False
        return callback in self.subscriptions[key]

    def publish(self, key, *args, **kwargs):
        """ override from cyrusbus enforcing simple callbacks as
            subscriptions (by default cyrusbus uses dictionaries)

        """
        if not self.has_any_subscriptions(key):
            return self

        for subscriber in self.subscriptions[key]:
            subscriber(self, *args, **kwargs)

    def subscribe(self, key, callback, force=False):
        """ override from cyrusbus forcing tuples, not lists.
             also changed return-value, now sends back all subscribers for <key>
        """
        if key not in self.public_keys():
            self[key] = tuple([callback])

        elif force or not self.has_subscription(key, callback):
            self[key] = self[key] + (callback,)
        return self[key]

class SelfHostingTupleBus(TupleBus):
    """ This class fools cyrusbus into using instances directly in the
        place of a simple dictionary -- convenient if your class already
        speaks the dictionary protocol.

            TODO: figure out how to *fully* reset..
    """
    def reset(self):
        self.subscriptions = self


class PostOffice(Service, Keyspace, SelfHostingTupleBus):
    """ PostOffice Service: a wrapper over cyrusbus's basic layout

          start: brief description of service start-up here
          stop:  brief description service shutdown here

        TODO: either wrap <publish> up in something asynchronous,
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

    def play(self):
        """ """
        return self

    def msg(self, *args, **kargs):
        """ TODO: determine caller function and dispatch to publish
        """
        NIY

    def start(self):
        """ """
        self.reset()
