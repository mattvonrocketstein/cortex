""" cortex.util.decorators.abstract

        # TODO: move this into an abstraction
        #caller = inspect.stack()[2]
        #frame  = caller[0]
        #traceback = inspect.getframeinfo(frame)
        #self.context = traceback.function
"""

import types

from cortex.util.decorators.data import DECORATION_ABORT_COMMAND
from cortex.util.decorators.data import AlreadyDecorated, DecoratorSetupError

class AbstractDecorator(object):
    """ Patterns in function decoration """

    def decorate(self, fxn):
        return fxn

    def _set_decorated_flag(self,fxn):
        """ mark function as decorated """
        try:
            setattr(fxn, '__decorated__', True)
        except AttributeError:
            # Called with a string?
            err  = " Cannot set __decorated__ label for object of type '{typ}'"
            err += ".\n\t\t(Did you call a decorator on something other than a function.. ?)"
            err  = err.format(typ=type(fxn).__name__)
            raise ValueError, err
        return fxn

    def __call__(self, fxn):
        """ connects or invokes various hooks for pre/post decoration,
             manages  various book-keeping.

            NOTE: do not override unless you have a good reason.
                  the actual decoration occurs in the call to
                  self.decorate
        """

        # pre-call may signal to abort further work,
        #  so first, check that out:
        command = self.pre_decoration_hook(fxn)
        if command == DECORATION_ABORT_COMMAND:
            return fxn

        # Mark it,
        #  Decorate it
        #   Record the event
        self._set_decorated_flag(fxn)
        new_fxn = self.decorate(fxn)
        self.memory = self.memory.union([fxn])

        # not every decorator mutates,
        #  some only annotate, so don't
        #   force subclasses to return a fxn
        new_fxn = new_fxn or fxn

        # try to define <inversion> and store it in the function,
        #  so that the function is capable of undecorating itself
        setattr(fxn, 'xfunc_undecorate', lambda: self.inversion(fxn))
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
        """
            NOTE:
        """
        # memory: a record of the work this factory has done
        self.memory = set([])
        self._init_with_args(*args)
        self._init_with_kargs(**kargs)

    def _init_with_args(self, *args):
        """ default is a noop"""
        pass

    def _init_with_kargs(self, **kargs):
        """ default is a noop"""
        pass

class MutationDecorator(AbstractDecorator):
    """ TODO: NIY """

    def decorate(self, fxn):
        """ """
        decoration = getattr(self,'decoration',None)
        assert decoration, "MutatingDecorator must define decoration"
        self.fxn = fxn

        # patch it to look more like the original
        #self.decoration.func_name = fxn.func_name
        #self.decoration.__doc__  = fxn.__doc__

class SimpleAnnotator(AbstractDecorator):
    """ see also: tokenfactory
        NOTE: by default only supports assignment with StringTypes,
              you can override that by subclasses and defining "allowed_types"
    """
    def _init_with_args(self, value_to_set):
        allowed_types = getattr(self, 'allowed_types', types.StringTypes)
        if not isinstance(value_to_set, allowed_types):
            err = 'To use "{kls}", you should call it with a single string that youd like to store.'
            err = err+'\n\tInstead, got: {actual}'.format(actual=str(value_to_set)
                                                        ,kls=self.__class__.__name__)
            raise DecoratorSetupError,err
        self.value_to_set = value_to_set
    def post_decoration_hook(self,fxn):
        setattr(fxn,self.label_name,self.value_to_set)

class StrictSimpleAnnotator(SimpleAnnotator):
    """ Same as SimpleAnnotator except that it enforces that
         the function may not have beeen previous Annotated. """

    def pre_decoration_hook(self, fxn):
        """ sanity checking """
        err    = "fxn@{fxn} has already been labeled at name {name} with {value}"
        current_value = getattr(fxn, self.label_name, None)
        format = dict(fxn=fxn, value=current_value)
        if current_value is not None:
            raise AlreadyDecorated, err.format(**format)
        return fxn
