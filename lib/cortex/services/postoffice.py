""" cortex.services.postoffice

      a simple service that exposes a message bus.

      TODO: (for json, pickles) annotate messages with data necessary to decode them?

"""

import simplejson

from cortex.core.util import report
from cortex.core.data import EVENT_T, ERROR_T
from cortex.core.ground import Keyspace
from cortex.services import Service
from cortex.core.bus import SelfHostingTupleBus

class channel(object):
    @classmethod
    def _bind(kls, postoffice):
        kls._bound=True
        kls._postoffice = postoffice

    @classmethod
    def _publish(kls, *args, **kargs):
        kargs.update(dict(__args=args))
        if not kls._bound: raise Exception, "channel is unbound"
        return kls._postoffice.publish(kls._label, **kargs)

    class __metaclass__(type):
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

        def __getattr__(kls, name):
            # only attributes not starting with "_" are organinzed
            # in the tree
            if not name.startswith("_"):
                return kls.__metaclass__.__new__(kls.__metaclass__, name, (channel, ),
                                                 dict(_label=name))
                #return self._d.setdefault(name, HierarchicalData())
            raise AttributeError("zzzzobject %r has no attribute %s" % (kls, name))


class PostOffice(Service, Keyspace, SelfHostingTupleBus):
    """ PostOffice Service:

          A wrapper over cyrusbus's basic layout that uses a
          key-value api to access the tuple-space described in
          cortex.core.ground.

          start: brief description of service start-up here
          stop:  brief description service shutdown here

          TODO: either wrap TupleBus.publish up in something asynchronous,
                or guarantee that subscriber-callbacks are themselves
                non-blocking.
    """
    ## Begin channel declarations (TODO: make this more like promela)
    notice = channel.NOTICE
    error = getattr(channel, ERROR_T)  # shortcut for publishing errors
    event  = getattr(channel, EVENT_T) # shortcut for publishing events

    @classmethod
    def enumerate_embedded_channels(kls):
        """ derives the channels embedded
            in this kls by way of inspection """
        matches = []
        for name in dir(kls):
            obj = getattr(kls,name)
            if hasattr(obj,'_bound'): #HACK
                matches.append(obj)
        return matches

    def __init__(self, *args, **kargs):
        """ """
        Service.__init__(self, *args, **kargs)
        default_name   = 'PostOffice::{_id}::keyspace'.format(_id=str(id(self)))
        keyspace_name  = self.universe or default_name
        keyspace_owner = self
        Keyspace.__init__(self, keyspace_owner, name=keyspace_name)
        SelfHostingTupleBus.__init__(self) # will call self.reset()
        #self.event.bind(self)
        for chan in self.enumerate_embedded_channels():
            chan._bind(self)

    def publish_json(self, label, data):
        """ publish as json """
        self.publish(label, simplejson.dumps(data))

    def publish_pickle(self, label, data):
        """ publish as pickle """
        self.publish(label, pickle.dumps(data))

    def msg(self, *args, **kargs):
        """ push a caller labeled message on to the stack.
            determines caller function and dispatches to publish """
        caller = whosdaddy()
        self.publish(caller['name'], (args, kargs))

    def start(self):
        """ """
        super(Service, self).start()
        self.reset()

class ParanoidPostOffice(PostOffice):
    """ ParanoidPostOffice Service
          Same as PostOffice, but with more restricted access to
          the <publish> operation.
    """

    do_not_discover = True

    def start(self):
        raise Exception,NIY
