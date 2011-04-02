""" cortex.core.metaclasses
"""

import types

class ClassTracking(type):
    """ """
    registry = {}
    def __new__(mcls, name, bases, dct):
        """ Allocating memory for class """
        #raise Exception, mcls

        return type.__new__(mcls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        """ Initializing (configuring) class """
        mcls = cls.__metaclass__
        if name not in mcls.registry:
            mcls.registry[name] = []
        super(ClassTracking, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kargs):
        instance=super(ClassTracking, cls).__call__(*args, **kargs)
        return instance


    def test(cls):
        print ummm

class TokenFactory(ClassTracking):
    """ """
    allowed_types = types.StringTypes

    @staticmethod
    def new():
        """ factory for factory """
        class DynamicTokenFactory(object):
            __metaclass__= TokenFactory
        return DynamicTokenFactory

    def __call__(cls, token, *args, **kargs):
        mcls = cls.__metaclass__
        if not isinstance(token, mcls.allowed_types):
            raise Exception,'BadTokenType: {type}'.format(type=str(type(token)))
        if not cls.__name__ in mcls.registry:
            raise Exception,"Error with ClassTracking metaclass."
        mcls.registry[cls.__name__].append(token)
        return token

class test:
    __metaclass__ = ClassTracking
    def foo(self): print 3
