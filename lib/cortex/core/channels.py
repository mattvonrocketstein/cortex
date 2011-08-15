""" cortex.core.channels

      # channels work via an "exchange", and can't do much until
      # they are bound.  a channel is bound using chan.bind(some_exchange).
      # .  an exchange can be any
      # object, provided it obeys the dictionary protocol.
      >>> event._exchange
      <PostOffice-Service 174661484>
      >>> event._exchange[event.__name__]
      (<bound method Terminal.push_q of <Terminal-Service 175386220>>,)

      # for a bound channel, both the channel and the
      # exchange can answer questions about the subscribers
      >>> event.subscribers()
      (<bound method Terminal.push_q of <Terminal-Service 176017164>>,)
      >>> event._exchange[event.__name__]
      (<bound method Terminal.push_q of <Terminal-Service 176017164>>,)

      # you can build a subchannel on the fly
      >>> event.foo
      <CHAN-(EVENT_T::foo)>

      # subchannels are cached
      >>> foo_channel = event.foo
      >>> foo_channel == event.foo
      True

      # by default subchannels get the same exchange their parent has
      >>> event.foo._exchange==event._exchange
      True

      # channels can non-recursively enumerate their subchannels
      >>> event.subchannels()
      [<CHAN-(EVENT_T::foo)>]

      # push a message into the channel by simply calling it. by default,
      # channels should accept any number of arguments of any type.
      >>> event("testing")
      >>> event(str,object)
"""

class UnboundChannel(Exception): pass

class ChannelType(type):
    """ metaclass for channels """

    def __getattr__(kls, name):
        """ only attributes not starting with
            "_" are organized in the tree
        """
        FORBIDDEN = ['trait_names', # used by ipython tab completion
                     'bound','bind',
                     'subscribe', 'subscribers',
                     'subchannels',
                     '_getAttributeNames']
        ## This is the main channel class, accesses
        ## to it mean the accessor wants a new channel
        #  named ``name``.
        if kls.__name__=='Channel':
            if name not in FORBIDDEN and not name.startswith("_"):
                namespace = dict(_label=name,)
                bases     = (channel, )
                mcls      = kls.__metaclass__
                return kls.__metaclass__.__new__(mcls, name, bases, namespace)
            raise AttributeError("ChannelType: %r has no attribute %s" % (kls.__name__, name))

        ## This is a class with Channel somewhere in it's ancestry,
        ## if it's bound, then make a bound subchannel, otherwise yell
        else:
            if kls._bound:
                if name in FORBIDDEN or '(' in name:
                    raise AttributeError("ChannelType: %r has no attribute %s" % (kls.__name__, name))
                subchan = getattr(channel, kls._label + '::' + name)
                subchan.bind(kls._exchange)
                return subchan
            else:
                raise UnboundChannel("cannot subchannel an unbound channel")

    def __new__(mcls, name, bases, dct):
        """ called when initializing (configuring)
            class, this method caches known instances
        """

        # Don't mess with the abstract class.
        if name=='Channel':
            return type.__new__(mcls, name, bases, dct)

        # For everything else, create it or grab it from the cache
        reg = getattr(mcls, 'registry', {})
        dct.update(dict(_bound=False))
        if name not in reg: reg[name] = type.__new__(mcls, name, bases, dct)
        else:               return reg[name]
        mcls.registry = reg
        return reg[name]

    def __call__(kls, *args, **kargs):
        """ shortcut for _publish """
        return kls._publish(*args, **kargs)

    @property
    def bound(self):
        return self._bound

    @property
    def name(kls):
        return kls.__name__.split('.')[-1]

    def __repr__(self):
        return '<CHAN-({c})>'.format(c=self.__name__)

def F(msg):
    """ makes a call-only-if-bound classmethodified
        function that, if the channel is unbound, displays
        error message ``msg`` instead of running ``func``
    """
    def if_bound(func):
        def new(kls, *args, **kargs):
            if kls._bound:
                try:
                    return func(kls, *args, **kargs)
                except Exception,e:
                    raise
            else:
                raise UnboundChannel, msg
        return classmethod(new)
    return if_bound

class Channel(object):
    """
        TODO: channel type declarations.. use linda?
    """

    __metaclass__ = ChannelType

    @F("cannot publish subscribers for an unbound channel")
    def subscribers(kls):
        return kls._exchange[kls.__name__]

    @F("cannot subscribe to an unbound channel")
    def subscribe(kls, callback):
        verify_callback(callback)
        return kls._exchange.subscribe(kls._label, callback)

    @F("cannot publish to a unbound channel")
    def _publish(kls, *args, **kargs):
        assert 'args' not in kargs,"'args' is reserved for internal use"
        kargs.update(dict(args=args))
        return kls._exchange.publish(kls._label, **kargs)

    @classmethod
    def unsubscribe(kls):
        kls._exchange.unsubscribe(kls._label)

    @classmethod
    def destroy(kls):
        kls.unsubscribe()
        del Channel.__metaclass__.registry[kls._label]
        return None

    @F("cannot query for subchannels on an unbound channel")
    def subchannels(kls):
        return [ item[1] for item in Channel.registry.items() \
                 if item[0].startswith(kls._label+'::') ]

    @classmethod
    def bind(kls, postoffice):
        """ a channel must be bound to operate """
        kls._bound      = True
        kls._exchange = postoffice
        return kls

channel=Channel

class ChannelManager(object):
    @classmethod
    def enumerate_embedded_channels(kls):
        """ derives the channels embedded
            in this kls by way of inspection
        """
        CHANNELS = getattr(kls, 'CHANNELS', [])
        if CHANNELS: return CHANNELS
        matches = []
        for name in dir(kls):
            obj = getattr(kls, name)
            if hasattr(obj,'_bound'): #HACK
                matches.append(obj)
        return matches

    def bind_embedded_channels(self):
        for chan in self.enumerate_embedded_channels():
            chan.bind(self)

def verify_callback(callback):
    """ ensure callback has a signature similar
        to one of these:
            def callback(ctx, **data):       stuff()
            def callback(self, ctx, **data): stuff()
    """
    import pep362
    import inspect
    try:
      s=pep362.signature(callback)
    except AttributeError: #used declare_channel?
      s=pep362.signature(callback.fxn)

    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    not_more_than2 = lambda s: len(s._parameters) < 3
    if2then_self_is_one = lambda s: ( len(s._parameters)!=2 and \
                                      True ) or \
                                    ( len(s._parameters)==2 and  \
                                      'self' in s._parameters ) or \
                                    False
    at_least_one = lambda s: len(s._parameters)>0
    assert (not s.var_args) and \
           not_more_than2(s) and\
           if2then_self_is_one(s) and \
           at_least_one(s) and \
           s.var_kw_args, 'callback@{name} needs to accept *args and **kargs'.format(name=s.name)

# TODO: move this into core.channels and formalize it
# standard unpacking method: special name "args" and everything but "args"
unpack = lambda data: ( data['args'],
                        dict([ [d,data[d]] for d in data if d!='args']) )

def declare_callback(channel=None):
    assert channel,"declare_callback decorator requires 'channel' argument"
    def decorator(fxn):
        fxn.declared_callback=1
        def bootstrap(self):
            if hasattr(self, 'subscribed'):
                return False
            else:
                from cortex.core.channels import ChannelType
                exchange = ChannelType.registry[channel]
                self.subscribed = 1
                k = new.instancemethod(fxn, self, self.__class__)
                setattr(self, fxn.__name__, k)
                exchange.subscribe(k)
                return self

        def new_function(self, ctx, **data):
            return fxn(self, ctx, **data)

        new_function.bootstrap=bootstrap
        new_function.declared_callback=1
        return new_function
    return decorator

def is_declared_callback(fxn):
    return hasattr(fxn, 'declared_callback')
import new
