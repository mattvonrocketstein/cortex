""" cortex.extensions.aima.logic

    small improvements, extensions, and syntactic sugar for aima.logic
    work with fewer strings, and fewer calls to Expr(), so it's more pythonic.

      e.g. this
        >>> is_definite_clause(expr('(Farmer(f) & Rabbit(r)) ==> Hates(f, r)'))

      becomes something more like this:
        >>> Farmer = predicate.Farmer; Rabbit=predicate.Rabbit; Hates = predicate.Hates
        >>> f = symbol.f; r = symbol.r
        >>> is_definite_clause(farmer(f) & Rabbit(r) >> Hates(f,r))


"""
from cortex.contrib.aima.logic import Expr, FolKB,expr,is_definite_clause

class Doctrine(FolKB):
    """  a Doctrine is a collection of beliefs.

         ask(q)::
           returns the first answer or False

         ask_generator(q)::
           yields all solutions with all symbols/values
           combinations in their own dictionary.

         consider(q, [with-respect-to])::
           yields all solutions as a flattened value,
           with respect to variable specified by  `wrt`
    """
    def consider(self, proposition, wrt=None):
        """ see Doctirne.__doc__ """

        results = self.ask_generator(proposition)
        if wrt is not None:
            for x in results:
                yield x[wrt]


class Expression(Expr):
    """ placeholder """
    pass

class _tmp(object):
    """ dumb helper to work with fewer strings"""
    def __getattr__(self, name):
        return Expression(name)

class symbol(_tmp):    pass
class predicate(_tmp): pass
predicate = predicate()
symbol    = symbol()

p = P = predicate
s = S = symbol

if __name__=='__main__':
    Farmer = predicate.Farmer
    Rabbit = predicate.Rabbit
    Hates  = predicate.Hates
    Wife  = predicate.Wife
    Mac = symbol.Mac
    Pete = symbol.Pete
    print (Farmer(Mac) & Rabbit(Pete) >> Hates(Mac,Pete))

    # A knowledge base consisting of first-order definite clauses
    kb0 = Doctrine( [ Farmer(Mac),
                      Rabbit(Pete),
                      ( Rabbit(s.r) &
                        Farmer(s.f) ) >>
                      Hates(s.f, s.r) ] )


    kb0.tell(Rabbit(s.Flopsie))

    # Flopsie
    print kb0.ask(Hates(Mac, s.x))[s.x]

    # should be False
    print kb0.ask(Wife(Pete, s.x))

    # should be [Pete, Flopsie]
    all_solutions = kb0.consider(Hates(Mac, s.x), s.x)
    print [z for z in all_solutions]
