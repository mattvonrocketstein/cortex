""" cortex.util.decorators.emits
"""

from cortex.util.decorators.function_annotator import FunctionAnnotator

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
        FunctionAnnotator.__init__(self, 'emits', signal=signal)

    def decorate(self, fxn):
        # returns None
        #FunctionAnnotator.decorate(self, fxn)

        def new_fxn(himself, *args, **kargs):
            result = fxn(*args, **kargs)
            if result is not None:
                report("publishing result because of emits decorator", self.signal, result)
                (himsef.universe|'postoffice').publish(self.signal, result)
            return result
        return FunctionAnnotator.decorate(self, fxn)
        return new_fxn

    def post_decoration_hook(self, fxn):
        """ """
        emits.table.append(fxn)

