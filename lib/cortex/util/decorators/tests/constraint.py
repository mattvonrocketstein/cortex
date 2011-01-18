""" cortex.util.decorators.tests.constraints
"""
import unittest

from cortex.util.decorators import constraint

class TestConstraint(unittest.TestCase):
    """
            >>> @constraint(labor="value")
            >>> def myfunction(stuff, other): pass
            >>> myfunction._constraint_labor == "value"
            True
            >>>
    """
    def test_constraint(self):
        """ tests whether two signals can coexit in function annotations """
        @constraint(label="value")
        @constraint(foo="bar")
        def function(): pass
        self.assertTrue(('label','value') in function.func_annotations)
        self.assertEqual(function._constraint_label, 'value')
        self.assertEqual(function._constraint_foo, 'bar')

if __name__ =='__main__':
    unittest.main()
