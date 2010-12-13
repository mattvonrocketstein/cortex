""" cortex.core.bus
"""

import datetime
from cyrusbus.bus import Bus

from cortex.core.util import report
from cortex.store.keyspace import Keyspace
from cortex.services import Service

# Imports for convenience
from cortex.util.decorators import handles_and_consumes_event
from cortex.util.decorators import handles_event
def summarize_event_system():
    """ """
    NIY

def event(label):
    new_event    = "EVENT_"+label.upper().replace(' ','_')
    event.EVENTS = event.EVENTS.union(set([new_event]))
    return new_event
event.EVENTS = set()

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
        #if key not in self.keys():
        if key not in self.public_keyskeys():
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

            # honor limits placed by csubscribe
            if subscriber in getattr(self,'consumers',[]):
                break

    def subscribe(self, key, callback, force=False):
        """ override from cyrusbus forcing tuples, not lists.

              NOTE: also changed return-value, now sends back
                    all subscribers for <key>
        """
        if key not in self.public_keys():
            self[key] = tuple([callback])
        elif force or not self.has_subscription(key, callback):
            self[key] = self[key] + (callback,)
        return self[key]

    def csubscribe(self, key, callback):
        """ consuming subscribe """
        consumers=getattr(self,'consumers',[])
        consumers.append(callback)
        self.consumers = consumers
        self.subscribe(key, callback)

    def xsubscribe(self, key, callback):
        """ exclusive subscribe """
        key = "__{key}::{time}__".format(key=key)
        assert self[key] not in self.public_keys()
        assert self[key] not in self.keys()
        self[key] =  tuple(callback,)
        return key

    xs = xsubscribe

class SelfHostingTupleBus(TupleBus):
    """ This class fools cyrusbus into using instances directly in the
        place of a simple dictionary -- convenient if your class already
        speaks the dictionary protocol.

            TODO: figure out how to *fully* reset..
    """
    def reset(self):
        self.subscriptions = self
