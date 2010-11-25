""" cortex.extensions.aima.logic

    extensions and improvements to aima.logic

"""
from cortex.contrib.aima.logic import Expr

class predicate(object):
    """ """
    def __getattr__(self, name):
        return Expr(name)

class symbol(object):
    """ """
    def __getattr__(self, name):
        return Expr(name)

predicate = predicate()
symbol    = symbol()

p = predicate
s = symbol
