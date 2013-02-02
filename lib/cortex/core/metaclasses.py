""" cortex.core.metaclasses

    Support for algebra amongst class objects, subclass enumeration.

"""
import new, copy
from collections import defaultdict

from goulash.util import uniq
from cortex.core.util import report

def metaclass_hook(func):
    func.metaclass_hook = True
    return staticmethod(func)

def dynamic_name(): return 'DynMix({U})'.format(U=uniq())

class META(type):
    """ the most generic metaclass..
        to avoid MRO issues, this should be the main one used,
        and everything should subclass it.

        Available hooks:
         *
         *
         *
    """
    def __lshift__(kls, my_mixin):
        """ algebra for left-mixin

             The following are equivalent:
              >>>  my_class = my_class << my_mixin
              >>>  class my_class(my_mixin, my_class): pass
        """
        my_mixin = copy.copy(my_mixin)
        my_mixin.__metaclass__ = META
        name  = dynamic_name()
        bases = tuple([my_mixin, kls])
        return type(name, bases, {})

    def __rshift__(kls, my_mixin):
        """ algebra for right-mixin:

             The following are equivalent:
              >>> my_class = my_class >> my_mixin
              >>> class my_class(my_class,my_mixin): pass
        """
        my_mixin = copy.copy(my_mixin)
        my_mixin.__metaclass__ = META
        name  = dynamic_name()
        bases = tuple([kls, my_mixin])
        return type(name, bases, {})

    def subclass(kls, name=None, dct={}, **kargs):
        """ dynamically generate a subclass of this class """
        dct = copy.copy(dct)#.copy()
        dct.update(kargs)
        if hasattr(kls, '_subclass_hooks'):
            name, dct = kls._subclass_hooks(name=name, **dct)
        name = name or "DynamicSubclassOf{K}_{U}".format(K=kls.__name__,
                                         U=uniq())
        # WOAH, this behaves differently than type()
        return new.classobj(name, (kls,), dct)

    @staticmethod
    def enumerate_hooks(mcls):
        """ returns a dictionary of metaclass hooks
            that will be run along with __new___
        """
        matches = [x for x in dir(mcls) if getattr(getattr(mcls, x, None),'metaclass_hook', False)]
        return dict( [ [match, getattr(mcls, match)] for match in matches ] )

    def __new__(mcls, name, bases, dct):
        """ simply reproduce the usual behaviour of type.__new__
            run any hooks (hooks are defined by subclassers)
        """
        class_obj = type.__new__(mcls, name, bases, dct)
        hooks = getattr(mcls, 'hooks', [])
        if not hooks:
            hooks = mcls.enumerate_hooks(mcls)
        for hook in hooks.values():
            hook(mcls, name, bases, dct, class_obj)
        return class_obj

class META1(META):
    """ a metaclass that tracks it's subclasses. """
    subclass_registry = defaultdict(lambda:[])

    @metaclass_hook
    def hook(mcls, name, bases, dct, class_obj):
        """ called when initializing (configuring) class,
            this method records data about hierarchy structure
        """
        mcls.subclass_registry[bases].append(class_obj)

    #@classmethod
    def template_from(this_kls, cls_template):
        """ return a new class that has all the behaviour specified in ``cls_template``
            as well as at least the minimum requirements of being an abstract Agent.

            ``cls_template`` is a dictionary-like item that has named behaviours
        """
        kls_name = '{outer}({inner})'.format(outer=this_kls.__name__,
                                             inner=cls_template.__name__)
        bases = (cls_template, this_kls)
        dct = {}
        return type(kls_name, bases, dct)

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
        assert kargs.keys() == ['namespace'],'only the namespace kw arg is defined'
        namespace = kargs.pop('namespace')
    else:
        namespace = {}
    name = 'DynamicallyGeneratedClassTracker'
    return META(name, bases, namespace)
