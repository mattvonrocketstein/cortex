""" cortex.services._bus
"""
from cyrusbus.bus import Bus

from cortex.core.util import report
from cortex.core.ground import Keyspace
from cortex.services import Service

class CortexBus(Service, Keyspace, Bus):
    """ CortexBus Service: thin wrapper over cyrusbus's basic layout
          start: brief description of service start-up here
          stop:  brief description service shutdown here
    """
    def __init__(self, *args, **kargs):
        Service.__init__(self, *args, **kargs)

        keyspace_name  = self.universe or 'CortexBus::keyspace'
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name)

        Bus.__init__(self) # will call self.reset()

    def reset(self):
        """ override from cyrusbus to replace a normal dictionary with
            the keyvalue wrapper over the lindypy-backed tuplespace
        """
        self.subscriptions = self

    def unsubscribe(self, key, callback=None):
        if callback==None:
            return self.subscriptions.remove(key)
        else:
            return Bus.unsubscribe(self,key,callback)
    def subscribe(self, key, callback, force=False):
        """ override from cyrusbus forcing tuples, not lists """
        print 'subscribing', key, callback
        if key not in self.subscriptions:
            self.subscriptions[key] = tuple(callback)

        subscription = {
            'key': key,
            'callback': callback
        }

        if force or not self.has_subscription(key, callback):
            self.subscriptions[key] = append(subscription)

        return self
    def start(self):
        return self.reset()

    def play(self):
        return self
