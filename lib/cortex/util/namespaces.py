""" cortex.util.namespaces
"""

from copy import copy
from inspect import isclass, ismethod, getsource
from inspect import isfunction, getargvalues

# begin helper functions
################################################################################
def summarize(namespace,func):
    """ summarize: a very common pattern over dictionaries """
    out = [ func(name,val) for name, val in namespace.items() ]
    return '\n'.join(out)

def frame2locals(_fr):
    """ Gets the locals() dictionary for a given frame """
    return getargvalues(_fr).locals

def classname(thing):
    "Return the fully-qualified class name of the specified class or object"
    try:
        return thing.__module__ + '.' + thing.__name__
    except:
        pass
    try:
        return thing.__module__ + '.' + thing.__class__.__name__
    except:
        _ty = str(type(thing))
        raise AssertionError('Must pass class or instance object, got'+_ty)

# begin classes
################################################################################
class NamespaceTests:
    """ Various boolean tests over objects, packaged thus to be resuable
          TODO: NamespaceTests(StaticMethodsOnly)
    """
    @classmethod
    def install_method(kls, method, name=None, aliases=[]):
        """ installs a new test into this class """
        name   = name or method.__name__
        assert not hasattr(kls,name), "Name already taken"
        method = staticmethod(method)
        setattr(kls, name, method)
        for alias in aliases:
            setattr(kls, alias, getattr(kls, name))

    @staticmethod
    def concrete(obj):
        return not NamespaceTests.abstract(obj)

    @staticmethod
    def abstract(obj):
        """ stab in the dark.. probably can't hurt
        """
        return getattr(obj,'_abstract',  False) or \
               getattr(obj,'__abstract', False) or \
               (getattr(obj,'Meta',None) and getattr(obj.Meta,'abstract',False)) or \
               (getattr(obj,'Meta',None) and getattr(obj.Meta,'_abstract',False)) or \
               (getattr(obj,'Meta',None) and getattr(obj.Meta,'__abstract',False)) or None


    @staticmethod
    def callable(obj):
        return hasattr(obj, '__call__')

    @staticmethod
    def isclass(obj):
        return isclass(obj)

    @staticmethod
    def name_startswith(obj, pattern):
            """ """
            return hasattr(obj,'__name__') and obj.__name__.startswith(pattern)

    @staticmethod
    def dictionaryish(obj):
            """ naive, but useful """
            return hasattr(obj,'keys') and hasattr(obj.keys,'__call__')

    @staticmethod
    def is_unittest_testcase_class(obj):
        """ """
        import unittest
        return isclass(obj) and issubclass(obj, unittest.TestCase)

    @staticmethod
    def is_django_testcase_class(obj):
        """ """
        from django.test import TestCase
        return isclass(obj) and issubclass(obj, TestCase) and not TestCase==obj


class NamespacePartition(object):
    """ NamespacePartion: introspective operations over dictionary-like objects

          NOTE: By default, all operations return dictionaries. Set
                dictionaries to False and you can get back another
                partion object.

          NOTE: This does not work in-place. (see the copy import up there?)
    """
    @ classmethod
    def from_module(kls, path, mod_name, **kargs):
       ns  = {}
       exec('from ' + path + ' import ' + mod_name + ' as mod', ns)
       mod = ns['mod']
       n = Namespace(mod.__dict__, **kargs)
       return n

    def __init__(self, namespace,dictionaries=True):
        """ """
        if not NamespaceTests.dictionaryish(namespace):
            if not hasattr(namespace,'__dict__'):
                err = "Namespace Partitioner really expects something like a dictionary, got {type}".format(type=type(namespace).__name__)
                raise TypeError, err
            namespace = namespace.__dict__
        self.namespace = namespace
        self.dictionaries = dictionaries

    def __add__(self, other):
        """ Update this namespace with another.

            works for all combinations of dict+namespace,
            namespace+dict, namespace+namespace.  if any of the
            constituents are or want to return dictionaries,
            return type will be dictionaries.
        """
        out = copy(self.namespace)
        if isinstance(other, NamespacePartition):
            out.update(other.namespace)
        elif isinstance(other,dict):
            out.update(other)
            return out

        if self.dictionaries or other.dictionaries:
            return out

        return NamespacePartition(out, dictionaries=False)



    def __iter__(self):
        """ dictionary compat """
        return iter(self.namespace)

    def doit(self):
        """ useful after you've invoked this with "dictionaries=False" to chain
            queries, but, at the end you want a dictionary again.
        """
        return self.namespace

    def items(self):
        """ dictionary compat """
        return self.namespace.items()

    @property
    def cleaned(self):
         """ """
         return self.clean()

    @property
    def unittest_testcases(self):
        """ Filter unittest test cases """
        return self.generic(NamespaceTests.is_unittest_testcase_class)

    @property
    def django_testcases(self):
        """ Filter django test cases """
        return self.generic(NamespaceTests.is_django_testcase_class)

    @property
    def functions(self):
        """ Filter functions """
        return self.generic(isfunction)

    @property
    def methods(self):
        """ Filter methods """
        return self.generic(ismethod)

    def clean(self, pattern='_'):
        """ For dictionary-like objects we'll clean out names that start with
            pattern.. for generic objects, we'll turn them into namespace
            dictionaries and proceed.
        """
        namespace = copy(self.namespace)
        bad_names = [x for x in namespace.keys() if x.startswith(pattern)]
        [ namespace.pop(name) for name in bad_names ]
        if self.dictionaries:
            return namespace
        else:
            return NamespacePartition(namespace)

    def startswith(self, string):
        """
        """
        test = NamespaceTests.name_startswith
        partial = lambda obj: test(obj,string)
        return self.generic(partial)

    def callables(self):
        return self % Namespace.Tests.callable

    def copy(self):
        """ This can fail for a variety of reasons involving thread safety,
            etc.. hopefully this approach is reasonable. """
        try:
            return copy(self.namespace)
        except TypeError:
            return dict([[name, self.namespace[name]] for name in self.namespace])

    def keys(self):
        """ dictionary compatibility """
        return self.namespace.keys()

    def __mod__(self, test):
        return self.generic(test)

    def __getitem__(self, a_slice):
        """ iteratively partion this namespace in
            a certain order with a tests vector
        """
        #raise Exception,slice
        if True: #isinstance(a_slice,slice):
            first,second,third = a_slice.start, a_slice.stop, a_slice.step
            original = self.dictionaries
            tmp     = self
            tmp.dictionaries=False
            for test in [first,second,third]:
                if not test: continue
                tmp = tmp%test
                #tmp = tmp.generic(test)
            self.dictionaries = original
            tmp.dictionaries  = original
            return tmp
        else:
            return self[a_slice::]

    def generic(self, test):
        """ This is the main work-horse everyone else will chain back to. Given
            a test, this partitions the namespace around it.

              TODO: make this generic over keys too, not just values
              TODO: refactor this around inspect.getmemebers()
        """
        namespace = self.copy()

        for key, val in namespace.items():
            if not test(val):
                namespace.pop(key)
        if self.dictionaries: return namespace
        return NamespacePartition(namespace,dictionaries=self.dictionaries)
    generic_filter = generic
    filter=generic

    def type_equal(self,thing):
        """ filter by type """
        _ty = ( type(thing).__name__=='type' and thing) or type(thing)
        return self.generic(lambda obj: type(obj)==_ty)

    def subclasses_of(self, thing, strict=True):
        """ filter by subclass """
        kls = thing
        if not isclass(thing):
            kls = thing.__class__
        test = lambda obj: issubclass(obj,kls)
        return self.generic(test)

# Begin aliases, shortcuts
################################################################################
NamespacePartition.Tests = NamespaceTests
Namespace       = NSPart = NamespacePartitioner = NamespacePartition
clean_namespace = lambda namespace: NamespacePartition(namespace).cleaned
Tests           = NamespaceTests
