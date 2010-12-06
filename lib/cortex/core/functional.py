""" cortex.core.functional
"""

def NOOP(*args, **kargs):
    """ generic NOOP """
    pass

def IDENTITY(*args, **kargs):
    """ taking a stab at generic identity function """
    if args and kargs:
        return args, kargs
    return args or kargs
