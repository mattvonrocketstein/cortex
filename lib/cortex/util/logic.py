""" cortex.util.logic

      Mostly for augmenting/supporting/extending AIMA codes
"""

from cortex.core.data import IDENTITY

def first(vector, predicate=IDENTITY):
    """ return the first item evaluating to
        True in Vector w.r.t predicate
    """
    for item in vector:
        if predicate(item):
            return item
    return None
