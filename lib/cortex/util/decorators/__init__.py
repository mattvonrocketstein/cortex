""" cortex.util.decorators.__init__
"""
import inspect
from cortex.core.util import report
from cortex.util.decorators.abstract import StrictSimpleAnnotator
from cortex.util.decorators.function_annotator import FunctionAnnotator
from cortex.util.decorators.abstract import AbstractDecorator
from cortex.util.decorators.abstract import SingleArgumentDecorator

from cortex.util.decorators.wrappers import call_first_if_exists
from cortex.util.decorators.wrappers import call_after_if_exists
from cortex.util.decorators.wrappers import chain_after_if_exists

class recurse_with_reactor(AbstractDecorator):
    """ """
    def _init_with_args(self, timedelta):
        self.timedelta=timedelta

    def decorate(self, fxn):
        if hasattr(fxn, 'is_wrapped'): return fxn
        def function(himself, *args, **kargs):
            print 'calling fxn',fxn,timedelta
            next_call = lambda: function(himself, *args, **kargs)
            himself.universe.reactor.callLater(timedelta, next_call)
            result = fxn(himself, *args, **kargs)
            himself.universe.reactor.callLater(timedelta, next_call)
            return result
        print 'returning'
        function.is_wrapped=True
        return function

class emits(FunctionAnnotator):
    """ a special case of function annotation, usage example follows.

            >>> @emits("<SIGNAL>")
            >>> def myfunction(stuff, other):
            >>>     return something

        ( if <myfunction> returns something other
           than None it will raise the signal specified)
    """
    table = []

    def __init__(self, signal):
        from cortex.core.symbols import event
        self.signal = event(signal)
        FunctionAnnotator.__init__(self, 'emits', signal)

    def decorate(self, fxn):
        # returns None
        FunctionAnnotator.decorate(self, fxn)
        def new_fxn(himself, *args, **kargs):
            result = fxn(*args, **kargs)
            if result is not None:

                report("publishing result because of emits decorator", self.signal,result)
                (himsef.universe|'postoffice').publish(self.signal, result)
            return result
        return new_fxn

    def post_decoration_hook(self, fxn):
        """ """
        emits.table.append(fxn)

class constraint(FunctionAnnotator):
    """ a special case of function annotation, usage example follows.

            >>> @constraint(labor="value")
            >>> def myfunction(stuff, other): pass
            >>> myfunction._constraint_labor == "value"
            True
            >>>

        additionally, this class will store a
    """
    table = []

    def __init__(self, **labels_and_constraints):
        FunctionAnnotator.__init__(self, 'constraint',
                                   **labels_and_constraints)
    def constraints_on(self, fxn):
        pass

    def keys(self):
        return self.table

    def values(self):
        return [getattr(x,'_constraint_'+x) for x in self.table]

    def post_decoration_hook(self, fxn):
        """ """
        constraint.table.append(fxn)

class handles_event(StrictSimpleAnnotator):
    label_name = 'handles_event'
handle_event = handles_event
handles      = handle_event

class handles_and_consumes_event(StrictSimpleAnnotator):
    label_name = 'handles_and_consumes_event'
handle_and_consume   = handles_and_consumes_event
handles_and_consumes = handles_and_consumes_event
