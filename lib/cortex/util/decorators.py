""" cortex.util.decorators
"""

def function_annotator(prefix, **function_metadata):
    """ loads function up with key-values
    """

    def decorator(fxn):
        """ """
        for label,val in function_metadata.items():
            setattr(fxn, '_'+prefix+'_'+label, val)

        # store an inversion and summary function
        fxn.remove_annotations  = lambda: [ delattr(fxn, '_'+prefix+'_', val) for val in function_metadata ]
        fxn.summary_annotations = lambda: [ '_'+prefix+'_' for val in function_metadata ]

        return fxn
    return decorator

def constraint(**labels_and_constraints):
    """ a special case of function annotation, usage example follows.

            >>> @constraint(kindness="dont hit people in the face")
            >>> def myfunction(stuff, other): pass
            >>> myfunction._constraint_kindness == "dont hit people in the face"
            True
            >>>
    """
    return function_annotator('constraint', **labels_and_constraints)
