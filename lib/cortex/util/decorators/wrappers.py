""" cortex.util.decorators.wrappers
"""
from cortex.util.decorators.abstract import SingleArgumentDecorator


class call_first_if_exists(SingleArgumentDecorator):
    def decorate(self, fxn):
        def function(himself, *args, **kargs):
            if hasattr(himself, self.main_argument):
                call_first = getattr(himself, self.main_argument)
                call_first(*args, **kargs)
            return fxn(himself, *args, **kargs)
        return function

class call_after_if_exists(SingleArgumentDecorator):
    def decorate(self, fxn):
        def function(himself, *args, **kargs):
            out = fxn(himself,*args, **kargs)
            if hasattr(himself, self.main_argument):
                call_after = getattr(himself, self.main_argument)
                call_after(*args, **kargs)
            return out
        return function
