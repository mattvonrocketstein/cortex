""" cortex.util.decorators.wrappers
"""
from cortex.util.decorators.abstract import SingleArgumentDecorator


class call_first_if_exists(SingleArgumentDecorator):
    """ NOTE:  intended for use with instance methods.

        USAGE: given a name, will search for that funcction
               (inside the same object) and call it before the
               decorated method is called.  if the function
               is not found, continues silently.  the named
               function will always be called with the same
               arguments as the decorated function.  the
               return value of the original function is
               preserved.

                class example:
                    def pre_foo(self):  print "PRE FOO"
                    def post_foo(self): print "POST FOO"

                    @call_first_if_exists('pre_foo')
                    def foo(self):      print "FOO"

    """
    def decorate(self, fxn):
        def function(himself, *args, **kargs):
            if hasattr(himself, self.main_argument):
                call_first = getattr(himself, self.main_argument)
                call_first(*args, **kargs)
            return fxn(himself, *args, **kargs)
        return function

class call_after_if_exists(SingleArgumentDecorator):
    """ NOTE:  intended for use with instance methods.
        NOTE:  intended for use with instance methods.
        USAGE: given a name, will search for that funcction
               (inside the same object) and call it after the
               decorated method is called.  if the function
               is not found, we continue silently.  the "named
               function" will always be called with the same
               arguments as the decorated function.  the
               return value of the original function is
               preserved.

                class example:
                    def pre_foo(self):  print "PRE FOO"
                    def post_foo(self): print "POST FOO"

                    @call_first_if_exists('pre_foo')
                    @call_after_if_exists('post_foo')
                    def foo(self):      print "FOO"
    """
    def decorate(self, fxn):
        def function(himself, *args, **kargs):
            out = fxn(himself,*args, **kargs)
            if hasattr(himself, self.main_argument):
                call_after = getattr(himself, self.main_argument)
                call_after(*args, **kargs)
            return out
        return function

class chain_after_if_exists(SingleArgumentDecorator):
    """ NOTE:  intended for use with instance methods.
        USAGE:

    """
    def _init_with_kargs(starmap=False, starstarmap=False):
        pass

    def decorate(self, fxn):
        def function(himself, *args, **kargs):
            out = fxn(himself, *args, **kargs)
            if hasattr(himself, self.main_argument):
                call_after = getattr(himself, self.main_argument)
                out = call_after(out)
            return out
        return function
chain_forward_if_exists = chain_after_if_exists
feed_forward_if_exists  = chain_after_if_exists
