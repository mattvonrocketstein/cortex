"""
"""

class Belief(object):
    """ a belief is an artifact in temporal logic.  see Shoham:1993
        for more information.  in his description, both `at` and `about`
        are time-valued, and `sentence` is potentially recursive.  That
        is to say, beliefs can be nested to represent a belief about a
        belief.
    """
    def __init__(self, at, about, sentence):
        """ see Belief.__doc__ """
