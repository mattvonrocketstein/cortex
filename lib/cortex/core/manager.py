""" cortex.core.manager

      Manager pattern stuff
"""

import datetime
import inspect
from contextlib import contextmanager

from types import StringTypes
from cortex.core.util import report
from cortex.core.hds import HierarchicalData

class Manager(object):
    """ Managers are inspired by django's managers.  Think of
        this class as a collection of patterns in tracking,
        reporting, and order statistics.  Example usage follows.

          Build an empty manager, or initialize it with some data
            >>> person_manager = Manager()
            >>> person_manager = Manager(**data) # Not implemented yet

          A person as a named collection of attributes:
            >>> jenny_attrs = dict(name='Jenny', phone=8675309, button=lambda x: x)

          Use <Manager> to wrap it
            >>> jenny = person_manager.register('jenny', jenny_attrs)

          Use lazy attributes as implicit data store (these examples are equivalent)
            >>> person_manager['jenny'].random.extra.data = {1:1,2:2,'whatever:''}
            >>> person_manager.jenny.random.extra.data = {1:1,2:2,'whatever:''}
            >>> jenny.random.extra.data = {1:1,2:2,'whatever:''}


         NOTE: if subclasses define 'asset_class', then it will be used in place of
               the default class <HierarchicalData>
    """
    class Duplicate(Exception): pass

    class NotFound(Exception): pass

    def __init__(self, *args, **kargs):
        """
             NOTE: subclasses are discouraged from using args..
                   why not be a good chap and use kargs instead?
        """
        self._pending   = []
        self.registry   = {}

        # generic storage for the actual manager itself.
        self.generic_store = HierarchicalData()

    def resolve_boot_order(self, **kargs):
        """ by default, simply returns the names in the same order
            they were registered.  subclassers may want to change
            this.
        """
        return [ pending[0] for pending in self._pending ]

    def load(self):
        """ Determines prerequisites with <solve_boot_order>, and feeds that
            value to <load_items>.

            Convention:
              calling <load> means that all the declarative "setup" calls
              to this manager have been completed.  in other words, if <manage>
              is used, this should be called after all calls to <manage> are
              finished.

              TODO: refactor
        """
        boot_order = self.resolve_boot_order()
        report('determined boot order:', boot_order)
        self.load_items(boot_order)

    def isloaded(self, obj):
        """ """
        trivially_true = (obj in self.registry.keys()) or \
                         (obj in self.registry.values())
        return trivially_true or (obj in [ x.obj for x in self.registry.values() ])
    is_loaded=isloaded

    def unload(self, obj):
        """ """
        if not isinstance(obj, StringTypes):
            # first, given any nonstring object try to find exact matches
            matches = filter(lambda x: x[1].obj == obj, self.registry.items())
            key = matches and matches[0][0]
            if key: return self.unload(key)
            else:
                # given a class, try to find matches with isinstance
                if inspect.isclass(obj):
                    #print obj, self.as_dict
                    matches = [ pair for pair in self.registry.items() if isinstance(pair[1].obj, obj)]
                    results = [ self.unload(x[0]) for x in matches ]
                    if not results:
                        err  = " Could not unload any objects of type: "+str(obj)
                        X = set([type(x) for x in self.registry.values()])
                        err += " Only these types of objects were found: "+str(X)
                        raise ValueError, err
                    return results
                else:
                    raise ValueError,"No value found for " + str(obj)

        # got a stringy key
        else:
            key = obj
            obj = self.registry[key]
            obj.obj.stop()
            del self.registry[key]
            return key


    def load_items(self, items):
        """ load_items calls load_item repeatedly for all the items
            pass in, but additionally enforces the bootstrapping order
        """
        for name in items:
            search = filter(lambda x: name == x[0], self._pending)
            if search:
                junk_name, kls, kls_kargs = search[0]
                kls_kargs = kls_kargs or {}
                self.load_item(kls=kls,
                               name=name,
                               kls_kargs=kls_kargs,
                               index=items.index(name))

    def load_item(self, name=None, kls=None, kls_kargs=None, index=None):
        """ loads an object from it's description, then registers it.

            load_item is called by Manager.load.
        """

        if name in self.registry:
            err='Duplicate entry found for "{name}": {entry}'
            err = err.format(entry=self[name], name=name)
            raise Manager.Duplicate(err)
        obj = self.load_obj(kls=kls, **kls_kargs)
        self.register(name,
                      obj = obj,
                      index = index,
                      kargs = kls_kargs)
        return obj

    def pre_load_obj(self, kls=None, **kls_kargs):
        """ pre_load_obj hook:
            must return description of (kls, kargs)
        """
        return kls, kls_kargs

    def load_obj(self, kls=None, **kls_kargs):
        """ load_obj: runs hooks and creates an object from the
            description of (kls, kargs).

            NOTE: if this is called directly, the object will not
                  be registered! you probably want to use <load_item>.
        """
        kls, kls_kargs = self.pre_load_obj(kls=kls, **kls_kargs)
        obj = kls(**kls_kargs)
        obj = self.post_load_obj(obj)
        return obj

    def post_load_obj(self, obj):
        """ post_load_obj hook:

            passed the object created by load_obj,
            this is a hook for manipulating it before
            it's returned.
        """
        # NOTE: this is used for agent.play()
        return obj

    def keys(self):
        """ dictionary compatability """
        return [x for x in self]

    def items(self):
        """ dictionary compatability """
        return self.registry.items()

    def values(self):
        """ dictionary compatability """
        return [x.obj for x in self.registry.values()]

    def __len__(self):
        """ list/dictionary compatibility """
        return len(self.registry)

    def asdf__getattr__(self, name):
        """ by default attributes are lazy
        """
        # Enforces privacy and special names
        special_names = ['asset_class']
        if name.startswith('_') or name in special_names:
            raise AttributeError, name

        try:
            return object.__getattribute__(self, '__getitem__')(name)
        except self.NotFound:
            return getattr(object.__getattribute__(self, 'generic_store'), name)

    def __getitem__(self, x):
        return self.registry[x].obj

    @property
    def last(self):
        """ All incoming assets should have been stamped;
            this function returns the oldest asset. """
        return self[self.as_list[-1]]

    @property
    def first(self):
        """ All incoming assets should have been stamped;
            this function returns the youngest asset.
        """
        return self[self.as_list[0]]

    def _stamp(self, name):
        """ Timestamps the asset with name <name>, safe
            to call multiple times, but dishonesty is
            discouraged.
        """
        self.registry[name].stamp = datetime.datetime.now()

    def pre_manage(self, name=None, kls=object, **kls_kargs):
        """ pre_manage hook:
              This function can modify the values, but must always
              return the ....  Default is a no-op.
        """
        return name, kls, kls_kargs

    def manage(self, name=None, kls=object, kls_kargs={}):
        """ This function queues up a pile of future assets and the arguments
            to initialize them with.  This pile will be dealt with when <load>
            is called.
        """
        name, kls, kls_kargs = self.pre_manage(name=name, kls=kls, **kls_kargs)

        self._pending.append([name, kls, kls_kargs])
        return name

    def post_manage(self):
        """ pre_manage hook:

              This function can modify the values, but must always
              return the ....  Default is a no-op.
        """
        return

    def post_registration(self, asset):
        """ post_registration hook:

              This function can modify the value, but must always
              return the new asset that is to be managed.  Default
              is a no-op.
        """
        return asset

    def pre_registration(self, name, **item_metadata):
        """ pre_registration hook:

              This function can modify the name, the item's metadata,
              or both, but it must always return (name, item_metadata).
              Default is a no-op.
        """
        return name, item_metadata

    def register(self, name, **item_metadata):
        """ register object <name> with namespace <item_metadata>
        """
        name, item_metadata = self.pre_registration(name, **item_metadata)
        name = str(name)
        self.registry[name] = getattr(self, 'asset_class', DEFAULT_ASSET_CLASS)()
        for key, value in item_metadata.items():
            setattr( self.registry[name], key, value)
        self._stamp(name) # sets birthday
        new_asset = self[name]
        new_asset = self.post_registration(new_asset)
        return new_asset

    def __str__(self):
        """ """
        return str( self.as_list )

    def __repr__(self):
        """ """
        return self.__class__.__name__ + '(' + str(self) + ')'

    def children(self):
        return [self[x].obj for x in self.as_list]

    def __getitem__(self, name):
        """ retrieve service by name
            Example:

               peers.as_list --> sorted by stamp, returns a list of names
               peers[int]    --> sorted by stamp, returns a HDS-Peer
               peers[str]    --> sorted by stamp, returns a HDS-Peer
               peers[peers[0]] --> returns the most recent HDS-Peer

            NOTE: currently case insensitive!
        """
        if isinstance(name, int):
            return self.registry[self.as_list[name]]

        if isinstance(name, str):
            for nayme in self.registry:
                if name.lower() == nayme.lower():
                    try:
                        return self.registry[name]
                    except KeyError,k:
                        if name!=name.lower():
                            return self.__getitem__(name.lower())
                        else:
                            raise k
            if name!=name.lower():
                return self.__getitem__(name.lower())
            else:
                raise self.NotFound('No such service: ' + name)

    @property
    def as_dict(self):
        """ dictionary morphology """
        return dict(self.items())

    @property
    def as_list(self):
        """ list morphology """
        out = [ x for x in self ]
        out.sort(lambda x, y: cmp(self.registry[x].stamp,
                                  self.registry[y].stamp))
        return out

    aslist = as_list

    def __iter__(self):
        """ list/dictionary compatibility: a dumb proxy """
        return iter(self.registry)

    @classmethod
    def choose_dynamic_name(kls):
        import uuid
        name = "Dynamic{k}Name{U}".format(U=str(uuid.uuid1()).split('-')[0],
                                         k=kls.__name__)
    @contextmanager
    def running(self, kls, **kargs):
        """ a contextmanager where __enter__ is "load/run the agent",
            with a return value of agent-handle and __exit__ is
            "unload the agent"

            TODO: think of a better name?
        """
        handle = self(kls, **kargs)
        yield handle
        self.unload(handle)

    def __call__(self, kls, name=None, **kargs):
        """ shortcut for load_item """
        # from cortex.core.util import getcaller
        if not hasattr(self, 'universe'):
            err = ("expected manager would know the universe by "
                   "the time it was asked to load something")
            raise ValueError, err
        #def uniq_name():
        #    raise Exception,'come on.. for now just pass the name'
        defaults = self.default_kls_kargs
        kargs.update(dict(name=name))# or uniq_name()))
        for k in defaults:
            if k not in kargs:
                kargs.update({k:defaults[k]})

        if name is None:
            name = self.choose_dynamic_name()
        loader = lambda:\
                 self.load_item(kls=kls,
                                name=name,
                                kls_kargs=kargs)
        #self.universe.reactor.callFromThread(loader)
        return loader()

    @property
    def default_kls_kargs(self):
        """ when __call__ is used, anything not appearing
            here and not in **kargs will be copied over. """
        return dict(universe=self.universe, name="DEFNAYME")

DEFAULT_ASSET_CLASS = HierarchicalData

class CortexManager(Manager): pass
