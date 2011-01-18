""" cortex.util.decorators.reactor_recursion
"""

from cortex.util.decorators.abstract import AbstractDecorator

class recurse_with_reactor(AbstractDecorator):
    """ """
    def _init_with_args(self, timedelta):
        self.timedelta = timedelta

    def decorate(self, fxn):
        if hasattr(fxn, 'is_wrapped'): return fxn
        def function(himself, *args, **kargs):
            #print 'calling fxn', fxn, self.timedelta
            next_call = lambda: function(himself, *args, **kargs)
            himself.universe.reactor.callLater(self.timedelta, next_call)
            result = fxn(himself, *args, **kargs)
            himself.universe.reactor.callLater(self.timedelta, next_call)
            return result
        #print 'returning'
        function.is_wrapped=True
        return function
