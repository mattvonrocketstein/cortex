""" cortex.util.decorators.function_annotator
"""

from cortex.util.decorators.abstract import AbstractDecorator

class FunctionAnnotator(AbstractDecorator):
    """ loads function up with key-values
        example usage:
           blue = FunctionAnnotator("label",color="Blue")
           @blue
           def fxn(arg1):
               pass
           fxn._label_blue==True
    """

    def _init_with_args(self, prefix):
        """ expecting: *args, from AbstractDecorator.__init__ """
        self._prefix           = prefix

    def _init_with_kargs(self, **function_metadata):
        """ expecting: **kargs, from AbstractDecorator.__init__ """
        self.function_metadata = function_metadata

    @property
    def prefix(self):
        """ format prefix """
        return '_' + self._prefix + '_'

    def remove_annotations(self, fxn):
        """ remove what we've done during decoration """

    def inversion(self, fxn):
        """ """
        self.remove_annotations(fxn)
        AbstractDecorator.inversion(self,fxn)

    def annotations(self, fxn):
        """ fxn as annotation dictionary:
              return all annotations on a given fxn """
        names = dir(fxn)
        test  = lambda x: x.startswith(self.prefix)
        out   = set([ tuple([x.replace(self.prefix,''), getattr(fxn, x)]) for x in names if test(x)])
        return out

    def decorate(self, fxn):
        """ """

        if not hasattr(fxn,'func_annotations'):
            fxn.func_annotations = fxn.func_annotations=set([])
        md = self.function_metadata.items()
        #print 'labeling', fxn,'with', md
        for label, val in md:
            setattr(fxn, self.prefix + label, val)
            fxn.func_annotations = fxn.func_annotations.union([tuple([label,val])])

            #fxn.func_annotations = property(lambda: self.annotations(fxn))
        # store an inversion and summary function..
        #  the <inversion> function will be stored by superclass
        fxn.func_remove_annotations  = lambda: self.remove_annotations(fxn)
        return fxn
