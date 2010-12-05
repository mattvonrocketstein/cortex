""" cortex.util.decorators
"""

DECORATION_ABORT_COMMAND = "randomjunkrandomjunk ABORT DECORATING FUNCTION randomjunkrandomjunk"

class AbstractDecorator(object):
    """ Patterns in function decoration """

    def __call__(self, fxn):
        """ does the actual decoration and adds hooks,
            do not override unless you have a good reason.
        """

        # precall may decide to abort, check that out
        command = self.pre_decoration_hook(fxn)
        if command==DECORATION_ABORT_COMMAND:
            return fxn


        setattr(fxn, '__decorated__', True)
        new_fxn = self.decorate(fxn)

        # not every decorator mutates,
        #  some only annotate, so don't
        #   force subclasses to return a fxn
        if new_fxn is None:
            new_fxn = fxn

        # try to define <inversion> and store it in the function,
        #  so that the function is capable of undecorating itself
        inversion = lambda: self.inversion(fxn)
        setattr(fxn, '__invert_decorator__', inversion)
        setattr(fxn, '__undecorate__', inversion)

        self.post_decoration_hook(fxn)
        return fxn

    def inversion(self, fxn):
        """ undo this decoration.

              In general this is tricky business, for a
              variety of reasons.  Subclasses may not be
              well behaved, or it may have side-effects that
              are not invertable.  For this to work best,
              subclasses should always chain back up here.

        """
        names = [ '__invert_decorator__',
                  '__undecorate__', '__decorated__',
                 ]
        for attr in names:
            if hasattr(fxn, attr):
                delattr(fxn,attr)

    def pre_decoration_hook(self, fxn):
        """ default is a noop"""
        pass

    def post_decoration_hook(self,fxn):
        """ default is a noop"""
        pass

    def __init__(self, *args, **kargs):
        """ """
        self.handle_args(args)
        self.handle_kargs(kargs)

    def handle_args(self, args):
        """ default is a noop"""
        pass

    def handle_kargs(self, kargs):
        """ default is a noop"""
        pass

class FunctionAnnotator(AbstractDecorator):
    """ loads function up with key-values """
    def __init__(self, prefix, **function_metadata):
        self._prefix           = prefix
        self.function_metadata = function_metadata

    @property
    def prefix(self):
        return '_' + self._prefix + '_'

    def remove_annotations(self, fxn):
        """ remove what we've done during decoration """
        [ delattr(fxn, self.prefix, val) for val in self.function_metadata ]
        delatr(fxn, 'summary_annotations')
        delatr(fxn, 'remove_annotations')

    def inversion(self, fxn):
        """ """
        self.remove_annotations(fxn)
        AbstractDecorator.inversion(self,fxn)

    def summary_annotations(self, fxn):
        return [ self.prefix + val for val in self.function_metadata ]

    def decorate(self, fxn):
        for label, val in self.function_metadata.items():
            setattr(fxn, '_' + self.prefix + '_'+label, val)

        # store an inversion and summary function..
        #  the <inversion> function will be stored by superclass
        fxn.remove_annotations  = lambda: self.remove_annotations(fxn)
        fxn.summary_annotations = lambda: self.summary_annotations(fxn)

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

    def decorate(self, fxn):
        """ """
        fxn.handles_event = self.event_name
        return fxn
