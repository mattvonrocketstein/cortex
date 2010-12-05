""" cortex.util.decorators.abstract

        # TODO: move this into an abstraction
        #caller = inspect.stack()[2]
        #frame  = caller[0]
        #traceback = inspect.getframeinfo(frame)
        #self.context = traceback.function
"""

from cortex.util.decorators.data import DECORATION_ABORT_COMMAND

class AbstractDecorator(object):
    """ Patterns in function decoration """
    def decorate(self,fxn):
        return fxn

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


class MutationDecorator(AbstractDecorator):
    """ """

    def decorate(self, fxn):
        """ """
        decoration = getattr(self,'decoration',None)
        assert decoration, "MutatingDecorator must define decoration"
        self.fxn = fxn

        # patch it to look more like the original
        #self.decoration.func_name = fxn.func_name
        #self.decoration.__doc__  = fxn.__doc__
