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
                FORBIDDEN = ['trait_names','subchannels','_getAttributeNames']
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

def F(msg):
    """ makes a call-only-if-bound classmethodified
        function that, if the channel is unbound, displays
        error message ``msg`` instead of running ``func`` """
    def ifbound2(func):
        def new(kls, *args, **kargs):
            if kls._bound: return func(kls, *args, **kargs)
            else:          raise UnboundChannel, msg
        return classmethod(new)
    return ifbound2


class Channel(object):
    """ inspired by promela

        TODO: channel type declarations.. use linda?
    """
    __metaclass__ = ChannelType

    @F("cannot query for subchannels on an unbound channel")
    def subchannels(kls):
        return [x for x in Channel.registry.keys() if x.startswith(kls._label+'::')]

    @classmethod
    def _bind(kls, postoffice):
        """ a channel must be bound to operate """
        kls._bound=True
        kls._postoffice = postoffice

    @F("cannot publish to a unbound channel")
    def _publish(kls, *args, **kargs):
        kargs.update(dict(__args=args))
        if not kls._bound: raise Exception, "channel is unbound"
        return kls._postoffice.publish(kls._label, **kargs)
channel=Channel

class ChannelManager(object):
    @classmethod
    def enumerate_embedded_channels(kls):
        """ derives the channels embedded
            in this kls by way of inspection
        """
        matches = []
        for name in dir(kls):
            obj = getattr(kls, name)
            if hasattr(obj,'_bound'): #HACK
                matches.append(obj)
        return matches

    def bind_embedded_channels(self):
        for chan in self.enumerate_embedded_channels():
            chan._bind(self)
