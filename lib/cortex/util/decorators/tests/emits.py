""" cortex.util.decorators.tests.emits
"""
import unittest

from cortex.util.decorators import emits

class TestEmits(unittest.TestCase):
    def setUp(self):
        self.testing_signal1 = emits("testing1")
        self.testing_signal2 = emits("testing2")

    def test_emits2(self):
        """ tests whether two signals can coexit in function annotations """
        @self.testing_signal1
        @self.testing_signal2
        def function(): pass
        self.assertEqual(function.func_annotations,
                         set([('signal','testing1'),
                              ('signal','testing2'),]))

    def test_emits1(self):
        """ tests whether one signals appears function annotations """
        @self.testing_signal1
        def function(): pass
        self.assertEqual(function.func_annotations,
                         set([('signal','testing1')]))

if __name__ =='__main__':
    unittest.main()
