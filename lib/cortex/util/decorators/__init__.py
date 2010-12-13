""" cortex.util.decorators.__init__
"""
import inspect

from cortex.util.decorators.abstract import StrictSimpleAnnotator
from cortex.util.decorators.abstract import AbstractDecorator
from cortex.util.decorators.abstract import MutationDecorator
from cortex.util.decorators.function_annotator import FunctionAnnotator

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


class afterwards_emit(AbstractDecorator):
    """ """
    def __init__(self, event_name):
        """ """
        self.event_name = event_name

    def __call__(self, fxn):
        """
            from cortex.core.symbols import event
        """
        #raise Exception,fxn.__name__
        #AbstractDecorator.__call__(self, fxn)
        if getattr(fxn, '__decorated__', False):
            from cortex.util.namespaces import NamespacePartition
            print '='*80,NamespacePartition(fxn)

        from cortex.core.data import EVENT_T

        def new_fxn(*args, **kargs):
            """
            #(args[0].universe|'postoffice').publish(event(self.event_name), result)
            """
            result = fxn( *args, **kargs)
            (args[0].universe|'postoffice').publish(self.event_name, result)
            return result
        #if fxn.
        return new_fxn
