""" cortex.util.decorators.function_annotator
"""

from cortex.util.decorators.abstract import AbstractDecorator

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
