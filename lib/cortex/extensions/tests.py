""" cortex.extensions.tests
"""

import unittest

from cortex.contrib.aima.logic import expr, FolKB
from cortex.contrib.aima.logic import variables, fol_bc_ask,pretty

class LogicTest(unittest.TestCase):

    def setUp(self):
        """ """

    def test_extension(self):
        """ test more pythonic syntax for aima.logic's <expr> """
        from cortex.extensions.logic import p,s
        raw2 =  [p.Farmer(s.Mac),
                 p.Rabbit(s.Pete),
                 p.Mother(s.MrsMac, s.Mac),
                 p.Mother(s.MrsRabbit, s.Pete),
                 (p.Rabbit(s.r) & p.Farmer(s.f)) >> p.Hates(s.f, s.r),
                 (p.Mother(s.m, s.c)) >> p.Loves(s.m, s.c),
                 (p.Mother(s.m, s.r) & p.Rabbit(s.r)) >> p.Rabbit(s.m),
                 (p.Farmer(s.f)) >> p.Human(s.f),
                 (p.Mother(s.m, s.h) & p.Human(s.h)) >> p.Human(s.m),
                ]
        self._test_base(FolKB(raw2))

    def test_aima(self):
        """ with data taken from aima.logic """
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
        self._test_base(FolKB(map(expr, raw_data)))

    def _test_base(self,test_kb):
        """ adapted from aima.logic """
        self.assertEqual(self._test_ask('Farmer(x)',test_kb),   ['{x: Mac}'])
        self.assertEqual(self._test_ask('Human(x)',test_kb),    ['{x: Mac}', '{x: MrsMac}'])
        self.assertEqual(self._test_ask('Hates(x, y)',test_kb), ['{x: Mac, y: Pete}'])
        self.assertEqual(self._test_ask('Loves(x, y)',test_kb), ['{x: MrsMac, y: Mac}','{x: MrsRabbit, y: Pete}'])
        self.assertEqual(self._test_ask('Rabbit(x)',test_kb),   ['{x: MrsRabbit}', '{x: Pete}'])

    def _test_ask(self, q, test_kb):
        """ adapted from aima.logic, a tool to exercise
            the first-order-logic knowledge base
        """
        e = expr(q)
        vars = variables(e)
        ans = fol_bc_ask(test_kb, [e])
        res = []
        for a in ans:
            res.append(pretty(dict([(x, v) for (x, v) in a.items() if x in vars])))
        res.sort(key=str)
        return res

if __name__ =='__main__':
    unittest.main()
