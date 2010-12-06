""" cortex.store.mixins
"""
from cortex.core.util import report

def TupleSpaceFilterFactory(name):
    """ builds a property that represents jit
        executation of named-based filters """

    def dynamic_filter(self):
        """ """
        return self.filter(lambda tpl: tpl[0]==name)[0]
    dynamic_filter.__doc__ = "dynamic_filter(name)"
    return property(dynamic_filter)

class TransformerMixin(object):
    """ Memory interface morphology..
          Turns things into other things
    """
    def as_dht(self, name=None):
        """ NIY """
        return self.as_keyspace()

    def as_keyspace(self, name=None):
        """ TODO: use cortex.store.transform

            NOTE: this is a cheap, stupid, and possibly error-prone
                  cloning operation that is running.. but the alternative
                  is very expensive
        """
        from cortex.store.keyspace import Keyspace
        name = name or (self.name+':as:Keyspace')
        k = type('dynamicKeyspace', (Keyspace,),{})(self, name=name)
        k.__dict__  = self.__dict__
        #k.__dict__ = copy.copy(self.__dict__)
        return k

class SubspaceMixin(object):
    """ minor changes to support explicit named subspaces..
        still a work in progress
    """
    subspaces = TupleSpaceFilterFactory('__subspaces__')

    def install_subspace(self, other):
        """ TODO: ensure type(self)==type(other)?
            REFACTOR..
        """
        report('installing subspace "{other}" into '.format(other=other.name),self)

        #sanity check
        existential_test = lambda tpl: tpl[0] == other.name
        search_results   = self.filter(existential_test)
        if not search_results:

            # get subspaces, add this one to list
            subspaces = self.filter(lambda t: t[0]=='__subspaces__')
            if not subspaces:
                self.add('__subspaces__')
                return self.install_subspace(other)
            else:
                assert len(subspaces)==1
                subspaces=subspaces[0]
                subspaces=[x for x in subspaces]
                new_subspace =  subspaces + [other.name]
                subspaces = self.filter(lambda t: t[0]=='__subspaces__')[0]
                self.get(subspaces, remove=True)
                assert not self.filter(lambda t: t[0]=='__subspaces__'), 'was supposed to be removed..'
                self.add(tuple(new_subspace))
                data = new_subspace
        else:
            err = "Already a subspace by the name of {name} in {space}:"
            err = err.format(name=other.name,
                             space=self.name)
            report(err, search_results)
            return False, err

        # update subspace list
        #subspaces = self.subspaces + (other.name,)
        #
        #self.add(subspaces)

        report('finished installing subspace')
        return True, data
