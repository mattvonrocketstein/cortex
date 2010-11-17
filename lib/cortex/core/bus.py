""" cortex.core.bus
"""

from cyrusbus.bus import Bus

from cortex.core.util import report
from cortex.core.ground import Keyspace
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
