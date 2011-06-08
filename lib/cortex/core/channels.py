""" cortex.core.channels
"""

class UnboundChannel(Exception): pass

class ChannelType(type):
    """ metaclass for channels """

    def __getattr__(kls, name):
        """ only attributes not starting with
            "_" are organinzed in the tree """
        ## This is the main channel class, accesses
        ## to it mean the accessor wants a new channel
        #  named ``name``.
        if kls.__name__=='Channel':
            if not name.startswith("_"):
                namespace = dict(_label=name,)
                bases     = (channel, )
                mcls      = kls.__metaclass__
                return kls.__metaclass__.__new__(mcls, name, bases, namespace)
            raise AttributeError("ChannelType: %r has no attribute %s" % (kls.__name__, name))

        ## This is a class with Channel somewhere in it's ancestry,
        ## if it's bound, then make a bound subchannel, otherwise yell
        else:
            if kls._bound:
                FORBIDDEN = ['trait_names','bound','bind',
                             'subscribe',
                             'subchannels','_getAttributeNames']
                if name in FORBIDDEN or '(' in name:
                    raise AttributeError("ChannelType: %r has no attribute %s" % (kls.__name__, name))
                    #return kls.__dict__.get(name)
                subchan = getattr(channel, kls._label +'::'+name)
                subchan._bind(kls._postoffice)
                return subchan
            else:
                raise UnboundChannel,"cannot subchannel an unbound channel"

    def __new__(mcls, name, bases, dct):
        """ called when initializing (configuring)
            class, this method caches known instances
        """

        # Don't mess with the abstract class.
        if name=='Channel':
            return type.__new__(mcls, name, bases, dct)

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

def F(msg):
    """ makes a call-only-if-bound classmethodified
        function that, if the channel is unbound, displays
        error message ``msg`` instead of running ``func`` """
    def ifbound2(func):
        def new(kls, *args, **kargs):
            if kls._bound:
                try:
                    return func(kls, *args, **kargs)
                except Exception,e:
                    raise
            else:          raise UnboundChannel, msg
        return classmethod(new)
    return ifbound2

class Channel(object):
    """ inspired by promela

        TODO: channel type declarations.. use linda?
    """

    __metaclass__ = ChannelType

    @F("cannot subscribe to an unbound channel")
    def subscribe(kls, callback):
        verify_callback(callback)
        return kls._postoffice.subscribe(kls._label, callback)

    @F("cannot publish to a unbound channel")
    def _publish(kls, *args, **kargs):
        kargs.update(dict(args=args))
        return kls._postoffice.publish(kls._label, **kargs)

    @classmethod
    def unsubscribe(kls):
        kls._postoffice.unsubscribe(kls._label)

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
    def _bind(kls, postoffice):
        """ a channel must be bound to operate """
        kls._bound=True
        kls._postoffice = postoffice
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
            chan._bind(self)

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
    assert channel
    def decorator(fxn):
        fxn.declared_callback=1
        def bootstrap(self):
            if hasattr(self, 'subscribed'):
                return False
            else:
                from cortex.core.channels import ChannelType
                exchange = ChannelType.registry[channel]
                self.subscribed = 1
                k=new.instancemethod(fxn, self, self.__class__)
                setattr(self,fxn.__name__,k)
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
