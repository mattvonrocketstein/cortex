""" cortex.services._bus
"""

from cyrusbus.bus import Bus
from cortex.core.util import report
from cortex.core.ground import Keyspace
from cortex.services import Service

class PostOffice(Service, Keyspace, Bus):
    """ PostOffice Service: a thin wrapper over cyrusbus's basic layout
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """

    def __init__(self, *args, **kargs):
        """
        """
        Service.__init__(self, *args, **kargs)
        keyspace_name  = self.universe or 'CortexBus::keyspace'
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name)
        Bus.__init__(self) # will call self.reset()

    def reset(self):
        """ override from cyrusbus to replace a normal dictionary with
            the keyvalue wrapper over the lindypy-backed tuplespace
        """
        self.subscriptions = self # hack to make the bus use the Keyspace

    def unsubscribe(self, key, callback):
        if not self.has_subscription(key, callback):
            return self
        self[key] = tuple([cb for cb in self[key] if cb!=callback])

    def has_subscription(self, key, callback):
        """ override from cyrusbus """
        if key not in self.public_keys():
            return False
        return callback in self[key]

    def publish(self, key, *args, **kwargs):
        """ override from cyrusbus enforcing simple callbacks as subscriptions
        """
        if not self.has_any_subscriptions(key):
            return self

        for subscriber in self.subscriptions[key]:
            subscriber(self, *args, **kwargs)

    def subscribe(self, key, callback, force=False):
        """ override from cyrusbus forcing tuples, not lists
            also changed return-value, now sends all subscribers
        """
        subscription = callback

        if key not in self.public_keys():
            self[key] = tuple([subscription])

        elif force or not self.has_subscription(key, callback):
            self[key] = self[key] + (subscription,)
        return self[key]

    def start(self):
        return self.reset()

    def play(self):
        return self

    #keyspace_keys = Service.keys
