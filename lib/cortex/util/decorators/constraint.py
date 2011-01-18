""" cortex.util.decorators.constraint
"""

from cortex.util.decorators.function_annotator import FunctionAnnotator

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
