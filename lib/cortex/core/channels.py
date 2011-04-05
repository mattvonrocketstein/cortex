class ChannelType(type):

    def __getattr__(kls, name):
        # only attributes not starting with "_" are organinzed
        # in the tree
        if not name.startswith("_"):
            return kls.__metaclass__.__new__(kls.__metaclass__, name, (channel, ),
                                             dict(_label=name))
                #return self._d.setdefault(name, HierarchicalData())
        raise AttributeError("zzzzobject %r has no attribute %s" % (kls, name))

    def __new__(mcls, name, bases, dct):
            """ called when initializing (configuring) class,
                this method records data about hierarchy structure
            """
            if name=='channel':
                return type.__new__(mcls, name, bases, dct)
            reg = getattr(mcls, 'registry', {})
            dct.update(dict(_bound=False))
            if name not in reg: reg[name] = type.__new__(mcls, name, bases, dct)
            else:               return reg[name]
            mcls.registry = reg
            return reg[name]

    def __call__(kls, *args, **kargs):
            kls._publish(*args, **kargs)

class Channel(object):
    """ inspired by promela

        TODO: channel type declarations.. use linda?
    """
    __metaclass__ = ChannelType
    @classmethod
    def _bind(kls, postoffice):
        """ a channel must be bound to operate """
        kls._bound=True
        kls._postoffice = postoffice

    @classmethod
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
            obj = getattr(kls,name)
            if hasattr(obj,'_bound'): #HACK
                matches.append(obj)
        return matches

    def bind_embedded_channels(self):
        for chan in self.enumerate_embedded_channels():
            chan._bind(self)
