""" cortex.util.namespaces
      (previously django_debugging.inspection)
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
    @staticmethod
    def name_startswith(obj, pattern):
            """ """
            return hasattr(obj,'__name__') and obj.__name__.startswith(pattern)

    @staticmethod
    def dictionaryish(obj):
            """ """
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
Partion object.

NOTE: This does not work in-place. (see the copy import up there?)
"""
    def __init__(self, namespace,dictionaries=True):
        """ """
        if not NamespaceTests.dictionaryish(namespace):
            if not hasattr(namespace,'__dict__'):
                err = "Namespace Partitioner really expects something like a dictionary."
                raise TypeError, err
            namespace = namespace.__dict__
        self.namespace = namespace
        self.dictionaries = dictionaries

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
        return namespace

    def startswith(self, string):
        """
"""
        test = NamespaceTests.name_startswith
        partial = lambda obj: test(obj,string)
        return self.generic(partial)

    def copy(self):
        """ This can fail for a variety of reasons involving thread safety,
etc.. hopefully this approach is reasonable. """
        try:
            return copy(self.namespace)
        except TypeError:
            return dict([[name, self.namespace[name]] for name in self.namespace])

    def generic(self, test):
        """ This is the main work-horse everyone else will chain back to. Given
a test, this partitions the namespace around it.

TODO: refactor this around inspect.getmemebers()
"""
        namespace = self.copy()

        for key, val in namespace.items():
            if not test(val):
                namespace.pop(key)
        if self.dictionaries: return namespace
        return NamespacePartition(namespace,dictionaries=self.dictionaries)

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
NSPart = NamespacePartitioner = NamespacePartition
clean_namespace = lambda namespace: NamespacePartition(namespace).cleaned
Tests = NamespaceTests
