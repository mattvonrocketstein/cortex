""" cortex.core.bus
"""

from cyrusbus.bus import Bus

from cortex.core.util import report
from cortex.core.ground import NotFound

class TupleBus(Bus):
    """ a wrapper over cyrusbus to use tuples
         (by default it uses lists and dictionaries)
    """
    def unsubscribe_all(self, key):
        declare_unplugged = lambda cb: setattr(cb, 'unplugged', True)
        [ declare_unplugged(callback) for callback in self.subscriptions[key] ]
        print type(self.subscriptions)
        del self.subscriptions[key]

    def unsubscribe(self, key, callback=None):
        if callback is None:
            return self.unsubscribe_all(key)
        if not self.has_subscription(key, callback):
            return self
        self.subscriptions[key] = tuple([cb for cb in self.subscriptions[key] if cb!=callback])

    def has_subscription(self, key, callback):
        """ override from cyrusbus enforcing simple callbacks as
            subscriptions (by default cyrusbus uses dictionaries)
        """
        if key not in self.keys():
            return False
        subs=self.subscriptions[key]
        if subs==NotFound:
            return False
        return callback in subs

    def has_any_subscriptions(self, key):
        """ HACK: sidestepping problem with NotFound """
        if key in self.subscriptions:
            subs = self.subscriptions[key]
            if hasattr(subs, '__len__'):
                return len(subs) > 0
        return False

    def publish(self, key, *args, **kwargs):
        """ override from cyrusbus enforcing simple callbacks as
            subscriptions (by default cyrusbus uses dictionaries)

            :: returns number of messages delivered
        """
        if not self.has_any_subscriptions(key):
            return self
        N = 0
        subscribers = self.subscriptions[key]

        if subscribers==NotFound:
            return N
        for subscriber in subscribers:
            #report(subscriber)
            subscriber(self, *args, **kwargs)
            N+=1
        return N

    def subscribe(self, key, callback, force=False):
        """ override from cyrusbus forcing tuples, not lists.
             also changed return-value, now sends back all subscribers for <key>
        """
        if not callable(callback):
            raise TypeError,"Expected callback would be callable:" + str(callback)

        if key not in self.public_keys():
            self[key] = tuple([callback])

        elif force or not self.has_subscription(key, callback):
            result  = self[key]
            result  = result!=NotFound and result or tuple() # HACK
            result += (callback,)
            self.subscriptions[key] = result

        return self[key]

class SelfHostingTupleBus(TupleBus):
    """ This class fools cyrusbus into using instances directly in the
        place of a simple dictionary -- convenient if your class already
        speaks the dictionary protocol.

            TODO: figure out how to *fully* reset..
    """
    def reset(self):
        self.subscriptions = self
