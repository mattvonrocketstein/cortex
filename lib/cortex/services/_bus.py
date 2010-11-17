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

    def has_subscription(self, key, callback):
        if key not in self.public_keys():
            return False
        subscription = {'key': key, 'callback': callback}
        return subscription in self[key]

    def subscribe(self, key, callback, force=False):
        """ override from cyrusbus forcing tuples, not lists """
        report ('subscribing', dict(key=key, callback=callback,subscriptions=self.subscriptions,flush=True))
        report ('all keys',[x for x in self.public_keys()])
        report ('this key',self[key])

        if key not in self.public_keys():
            self[key] = (None,)

        subscription = { 'key':key, 'callback':callback }
        if force or not self.has_subscription(key, callback):
            print '-'*80, self[key],(subscription,)

        return self

    def start(self):
        return self.reset()

    def play(self):
        return self
