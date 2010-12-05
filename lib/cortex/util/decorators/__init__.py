""" cortex.util.decorators.__init__
"""
from cortex.util.decorators.abstract import AbstractDecorator
from cortex.util.decorators.function_annotator import FunctionAnnotator

class MutatingDecorator(AbstractDecorator):
    """ """
    pass

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

class handles_event(AbstractDecorator):
    """ """
    def __init__(self, event_name):
        self.event_name = event_name

    def pre_decoration_hook(self, fxn):
        """ sanity checking """
        err = "fxn@{fxn} has already been labeled as handling event called {event}"
        format=dict(fxn=fxn, event=getattr(fxn,'handles_event',None))
        assert not hasattr(fxn,'__handles_event'),err.format(**format)

    def replacement_function(*args, **kargs):
        pass

    def decorate(self, fxn):
        """ """
        fxn.handles_event = self.event_name
        return fxn
