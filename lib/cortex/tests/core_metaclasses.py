""" cortex.tests.core_metaclasses
"""

from unittest import TestCase

from cortex.core.agent import Agent
from cortex.tests import uniq

class MetaclassesTest(TestCase):
    def test_uniq(self):
        A = Agent.subclass()
        B = Agent.subclass()
        self.assertTrue( A != B )
        B.foo='bar'
        self.assertTrue( not hasattr(A,'foo') )

    def test_collide(self):
        class A(Agent.subclass(name='ProtoA')): pass
        B = Agent.subclass(name='B', foo='bar')
        C = Agent.subclass(bar='foo')
        self.assertTrue(not hasattr(Agent, 'foo'))
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        self.assertTrue(A!=B)
        self.assertTrue(not hasattr(A, 'foo'))
        self.assertTrue(not hasattr(C, 'foo'))
        self.assertTrue(hasattr(B,'foo'))

    def test_subclasses_empty(self):
        x = Agent.subclass(); self.assertTrue(issubclass(x, Agent))

    def test_subclasses_name(self,name=None):
        name = name or uniq()
        x = Agent.subclass(name); self.assertTrue(issubclass(x, Agent))
        self.assertTrue(x.__name__==name)

    def test_subclasses_dct(self, name=None):
        name = name or uniq()
        x = Agent.subclass(); self.assertTrue(issubclass(x, Agent))
        x = Agent.subclass(name , dict(foo=3));
        self.assertTrue(x.__name__==name)
        self.assertTrue(x.foo==3)

    def test_subclasses_dct2(self, name=None):
        name = name or uniq()
        x = Agent.subclass(); self.assertTrue(issubclass(x, Agent))
        x = Agent.subclass(name, foo=3);
        self.assertTrue(x.__name__==name)
        self.assertTrue(x.foo==3)

    def test_subclasses_multiple(self):
        x = Agent.subclass();
        y = Agent.subclass();
        self.assertTrue(issubclass(x, Agent))
        self.assertTrue(issubclass(y, Agent))
        self.assertTrue(not issubclass(y, x))
        self.assertTrue(not issubclass(x, y))
