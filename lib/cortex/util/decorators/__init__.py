""" cortex.util.decorators.__init__
"""
import inspect
from cortex.core.util import report
from cortex.util.decorators.abstract import StrictSimpleAnnotator
from cortex.util.decorators.abstract import MutationDecorator
from cortex.util.decorators.function_annotator import FunctionAnnotator
from cortex.util.decorators.abstract import AbstractDecorator

class recurse_with_reactor(AbstractDecorator):
    def __init__(self, timedelta):
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

    def decorate(self,fxn):
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

            >>> @constraint(kindness="dont hit people in the face")
            >>> def myfunction(stuff, other): pass
            >>> myfunction._constraint_kindness == "dont hit people in the face"
            True
            >>>
    """
    table = []

    def __init__(self, **labels_and_constraints):
        FunctionAnnotator.__init__(self, 'constraint', **labels_and_constraints)

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
