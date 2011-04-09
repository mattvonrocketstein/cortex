""" cortex.tests.core_metaclasses
"""

from unittest import TestCase

from cortex.core.node import Agent

class MetaclassesTest(TestCase):
    def test_subclasses_empty(self):
        x = Agent.subclass(); self.assertTrue(issubclass(x, Agent))

    def test_subclasses_name(self):
        x = Agent.subclass('testing'); self.assertTrue(issubclass(x, Agent))
        self.assertTrue(x.__name__=='testing')

    def test_subclasses_dct(self):
        x = Agent.subclass(); self.assertTrue(issubclass(x, Agent))
        x = Agent.subclass('testing',dict(foo=3));
        self.assertTrue(x.__name__=='testing')
        self.assertTrue(x.foo==3)
