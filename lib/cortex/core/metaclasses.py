""" cortex.core.metaclasses
"""

import types

class ClassTracking(type):
    registry = {}
    def __new__(mcls, name, bases, dct):
        """ Allocating memory for class """
        #raise Exception, mcls
        if name not in mcls.registry:
            mcls.registry[name] = []
        return type.__new__(mcls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        """ Initializing (configuring) class """
        super(ClassTracking, cls).__init__(name, bases, dct)

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
