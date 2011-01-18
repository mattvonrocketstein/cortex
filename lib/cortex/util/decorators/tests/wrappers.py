""" cortex.util.decorators.tests.wrappers
"""
import unittest

from cortex.util.decorators import call_first_if_exists
from cortex.util.decorators import call_after_if_exists
from cortex.util.decorators import chain_after_if_exists

class kitchen_three:
    """ mock for test case """
    cleaned_dishes = False
    opened_fridge  = False
    callrecord     = []

    def pre_sandwich(self):
        """ things to do before the make_sandwich function """
        self.opened_fridge = True
        self.callrecord.append("PRE")


    def post_sandwich(self):
        """ things to do before the make_sandwich function """
        self.cleaned_dishes = True
        self.callrecord.append("POST")

    @call_first_if_exists('pre_sandwich')
    @call_after_if_exists('post_sandwich')
    def make_sandwich(self):
        """ before we can make a sandwich we need to open the fridge. """
        self.made_sandwich = True
        self.callrecord.append("SANDWICH")

class kitchen_two:
    """ mock for test case """
    cleaned_dishes = False

    def post_sandwich(self):
        """ things to do before the make_sandwich function """
        self.cleaned_dishes = True

    @call_after_if_exists('post_sandwich')
    def make_sandwich(self):
        """ before we can make a sandwich we need to open the fridge. """
        self.made_sandwich = True

class kitchen_one:
    """ mock for test case """
    opened_fridge = False

    def pre_sandwich(self):
        """ things to do before the make_sandwich function """
        self.opened_fridge = True

    @call_first_if_exists('pre_sandwich')
    def make_sandwich(self):
        """ before we can make a sandwich we need to open the fridge. """
        self.made_sandwich = True

class chain_testing:
    @chain_after_if_exists('send_two')
    def send_one(self):          return 1

    def send_two(self, ignored): return 2
    @chain_after_if_exists("send_b")
    def send_a(self): return "A"

class TestWrappers(unittest.TestCase):
    def test_chain_after(self):
        self.assertEqual(2, chain_testing().send_one())
        self.assertEqual("A", chain_testing().send_a())

    def test_call_after(self):
        k = kitchen_two()
        self.assertTrue(not k.cleaned_dishes)
        k.make_sandwich()
        self.assertTrue(k.cleaned_dishes)

    def test_call_first(self):
        k = kitchen_one()
        self.assertTrue(not k.opened_fridge)
        k.make_sandwich()
        self.assertTrue(k.opened_fridge)

    def test_both(self):
        k = kitchen_three()
        self.assertTrue(not k.opened_fridge)
        self.assertTrue(not k.cleaned_dishes)
        k.make_sandwich()
        self.assertTrue(k.opened_fridge)
        self.assertTrue(k.cleaned_dishes)
        self.assertEqual(k.callrecord,["PRE","SANDWICH","POST"])

if __name__ =='__main__':
    unittest.main()
