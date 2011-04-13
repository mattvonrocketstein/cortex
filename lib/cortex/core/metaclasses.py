""" cortex.core.metaclasses

    Support for algebra amongst class objects, subclass enumeration.

"""
import copy
import uuid
import types
from cortex.tests import uniq
def metaclass_hook(func):
    func.metaclass_hook=True
    return staticmethod(func)

def dynamic_name(): return 'DynMix({U})'.format(U=uniq())

class META(type):
    """ the most generic metaclass..
        to avoid MRO issues, this should be the main one used,
        and everything should subclass it and define hooks.
    """
    def __lshift__(kls,other_kls):
        """ algebra for left-mixin:
             my_class = my_class << my_mixin
        """
        other_kls = copy.copy(other_kls)
        other_kls.__metaclass__ = META
        name  = dynamic_name()
        bases = tuple([other_kls,kls])
        return type(name, bases, {})

    def __rshift__(kls, other_kls):
        """ algebra for right-mixin:
             my_class = my_class >> my_mixin
        """
        other_kls = copy.copy(other_kls)
        other_kls.__metaclass__ = META
        name  = dynamic_name()
        bases = tuple([kls, other_kls])
        return type(name, bases, {})

    def subclass(kls, name=None, dct={}, **kargs):
        """ dynamically generate a subclass of this class """
        import new
        import copy
        dct=copy.copy(dct)#.copy()
        dct.update(kargs)
        if hasattr(kls, '_subclass_hooks'):
            name,dct = kls._subclass_hooks(name=name, **dct)
        name = name or "DynamicSubclassOf{K}_{U}".format(K=kls.__name__,
                                         U=str(uuid.uuid1()).split('-')[-2])
        # WOAH, this behaves differently than type()
        return new.classobj(name, (kls,), dct)

    @staticmethod
    def enumerate_hooks(mcls):
        matches = [x for x in dir(mcls) if getattr(getattr(mcls,x,None),'metaclass_hook', False)]
        return [ getattr(mcls,match) for match in matches ]

    def __new__(mcls, name, bases, dct):
        """ simply reproduce the usual behaviour of type.__new__
            run any hooks (hooks are defined by subclassers)
        """
        class_obj = type.__new__(mcls, name, bases, dct)
        hooks = getattr(mcls, 'hooks', [])
        if not hooks:
            hooks = mcls.enumerate_hooks(mcls)
        for hook in hooks:
            hook(mcls, name, bases, dct, class_obj)
        return class_obj

class META1(META):
    """ a metaclass that tracks it's subclasses. """
    subclass_registry = {}

    @metaclass_hook
    def hook(mcls, name, bases, dct, class_obj):
        """ called when initializing (configuring) class,
            this method records data about hierarchy structure
        """
        subclass_registry = getattr(mcls, 'subclass_registry', None)
        if subclass_registry is not None:
            subclass_registry = mcls.subclass_registry
            if bases not in subclass_registry: subclass_registry[bases] = [ class_obj ]
            else:                subclass_registry[bases].append(class_obj)
            mcls.subclass_registry = subclass_registry

    def subclasses(kls, deep=False, dictionary=False, normalize=False):
            """ get subclasses for class """

            matches = []
            meta    = kls.__metaclass__

            # keep it simple stupid
            if not deep:
                for bases in meta.subclass_registry:
                    if kls in bases:
                        matches += meta.subclass_registry[bases]

            # use a bigger hammer..
            if deep:
                import operator
                matches = filter(lambda k: issubclass(k,kls),\
                                 reduce(operator.add, meta.subclass_registry.values()))

            # convert output to { subclass_name : subclass_object }
            if dictionary:
                matches = [ [m.__name__, m] for m in matches ]
                if normalize: matches = [ [x[0].lower(),x[1]] for x in matches]
                matches = dict(matches)
            return matches


"""
class ClassTracking(type):
    ''' '''
    registry = {}
    def __new__(mcls, name, bases, dct):
        ''' Allocating memory for class '''
        #raise Exception, mcls

        return type.__new__(mcls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        ''' Initializing (configuring) class '''
        mcls = cls.__metaclass__
        if name not in mcls.registry:
            mcls.registry[name] = []
        super(ClassTracking, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kargs):
        instance=super(ClassTracking, cls).__call__(*args, **kargs)
        return instance

class TokenFactory(ClassTracking):
    ''' '''
    allowed_types = types.StringTypes

    @staticmethod
    def new():
        ''' factory for factory '''
        class DynamicTokenFactory(object):
            __metaclass__= TokenFactory
        return DynamicTokenFactory

    def __call__(cls, token, *args, **kargs):
        mcls = cls.__metaclass__
        if not isinstance(token, mcls.allowed_types):
            raise Exception,'BadTokenType: {type}'.format(type=str(type(token)))
        if not cls.__name__ in mcls.registry:
            raise Exception,'Error with ClassTracking metaclass.'
        mcls.registry[cls.__name__].append(token)
        return token

class test:
    __metaclass__ = ClassTracking
"""
def subclass_tracker(*bases, **kargs):
    """ dynamically generates the subclass tracking class that extends ``bases``.

        often the name doesn't matter and will never be seen,
        but you might as well be verbose in case it's stumbled across.

        usually an empty dictionary is fine for the namespace.. after all you're
        specifying the bases already, right?

        Example usage follows:

          SomeService(classtracker(Service, Mixin1, Mixin2)):
               ''' function body '''

    """
    if kargs:
        assert kargs.keys()==['namespace'],'only the namespace kw arg is defined'
        namespace=kargs.pop('namespace')
    else:
        namespace = {}
    name = 'DynamicallyGeneratedClassTracker'
    return META(name, bases, namespace)
