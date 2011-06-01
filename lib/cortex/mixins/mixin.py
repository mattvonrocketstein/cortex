""" cortex/mixins/mixin """
class Mixin:

    @classmethod
    def bind_to(self, other):
        name = 'name(core)'.format(name=other.__name__,core=self.__name__)
        bases = (other)
        return type(name, bases, {})
