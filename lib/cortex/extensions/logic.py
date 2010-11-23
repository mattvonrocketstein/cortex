""" cortex.extensions.aima.logic

    extensions and improvements to aima.logic

"""
from cortex.contrib.aima.logic import expr, FolKB,variables, fol_bc_ask,pretty
raw_data =  ['Farmer(Mac)',
               'Rabbit(Pete)',
               'Mother(MrsMac, Mac)',
               'Mother(MrsRabbit, Pete)',
               '(Rabbit(r) & Farmer(f)) ==> Hates(f, r)',
               '(Mother(m, c)) ==> Loves(m, c)',
               '(Mother(m, r) & Rabbit(r)) ==> Rabbit(m)',
               '(Farmer(f)) ==> Human(f)',
               # Note that this order of conjuncts
               # would result in infinite recursion:
               #'(Human(h) & Mother(m, h)) ==> Human(m)'
               '(Mother(m, h) & Human(h)) ==> Human(m)'
        ]

class Symbol(object):
    """ """
    def __init__(self,path=''):
        self.path=path
    def __repr__(self): return self.path
    def __str__(self):  return self.path

class Predicate(object):
    def __init__(self,name=''):
        self.name=name
    def __repr__(self):
        return str(self)
    def __str__(self):
        if not hasattr(self,'args'):
            return self.name
        return self.name+'('+','.join([str(arg) for arg in self.args])+')'
    def __and__(self, other):
        return conjunction(self, other)

    def __call__(self,*args):
        self.args = args
        return self
    def __rshift__(self,other):
        return str(self) + ' ==> '+str(other)

class conjunction(object):
    def __init__(self, first, second,combinator='__and__'):
        self.first=first
        self.second=second
        self.combinator=combinator
    def __str__(self): return self.__repr__()
    def __rshift__(self, other):
        return str(self) +' ==> '+str(other)
    def __repr__(self):
        return str(self.first)+ ' & ' + str(self.second)

class predicate(object):
    """ """
    def __getattr__(self, name):
        return Predicate(name)

class symbol(object):
    """ """
    def __getattr__(self, name):
        return Predicate(name)

predicate=predicate();
p = predicate
symbol=symbol();       s = symbol

raw2 =  [p.Farmer(s.Mac),
         p.Rabbit(s.Pete),
         p.Mother(s.MrsMac, s.Mac),
         p.Mother(s.MrsMac, s.Mac),
         p.Mother(s.MrsRabbit, s.Pete),
         (p.Rabbit(s.r) & p.Farmer(s.f)) >> p.Hates(s.f, s.r),
         (p.Mother(s.m, s.c)) >> p.Loves(s.m, s.c),
         (p.Mother(s.m, s.r) & p.Rabbit(s.r)) >> p.Rabbit(s.m),
         (p.Farmer(s.f)) >> p.Human(s.f),
         (p.Mother(s.m, s.h) & p.Human(s.h)) >> p.Human(s.m)
        ]
print map(expr, raw_data)
print map(expr, map(str, raw2))
print '-'*80
def test_ask(q):
    e = expr(q)
    vars = variables(e)
    ans = fol_bc_ask(test_kb, [e])
    res = []
    for a in ans:
        res.append(pretty(dict([(x, v) for (x, v) in a.items() if x in vars])))
    res.sort(key=str)
    return res

test_kb = FolKB(
    map(expr, ['Farmer(Mac)',
               'Rabbit(Pete)',
               'Mother(MrsMac, Mac)',
               'Mother(MrsRabbit, Pete)',
               '(Rabbit(r) & Farmer(f)) ==> Hates(f, r)',
               '(Mother(m, c)) ==> Loves(m, c)',
               '(Mother(m, r) & Rabbit(r)) ==> Rabbit(m)',
               '(Farmer(f)) ==> Human(f)',
               # Note that this order of conjuncts
               # would result in infinite recursion:
               #'(Human(h) & Mother(m, h)) ==> Human(m)'
               '(Mother(m, h) & Human(h)) ==> Human(m)'
               ])
)

assert test_ask('Farmer(x)')==['{x: Mac}']
assert test_ask('Human(x)')==['{x: Mac}', '{x: MrsMac}']
assert test_ask('Hates(x, y)')==['{x: Mac, y: Pete}']
assert test_ask('Loves(x, y)')==['{x: MrsMac, y: Mac}', '{x: MrsRabbit, y: Pete}']
assert test_ask('Rabbit(x)')==['{x: MrsRabbit}', '{x: Pete}']
print '-'*80
