""" cortex.util.decorators.tests.wrappers
"""
import unittest

from cortex.util.decorators import call_first_if_exists
from cortex.util.decorators import call_after_if_exists


class kitchen_three:
    """ mock for test case """
    cleaned_dishes = False
    opened_fridge = False
    def pre_sandwich(self):
        """ things to do before the make_sandwich function """
        self.opened_fridge = True
        print "PRE"


    def post_sandwich(self):
        """ things to do before the make_sandwich function """
        self.cleaned_dishes = True
        print "POST"

    @call_first_if_exists('pre_sandwich')
    @call_after_if_exists('post_sandwich')
    def make_sandwich(self):
        """ before we can make a sandwich we need to open the fridge. """
        self.made_sandwich = True
        print "SAND"

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


class TestWrappers(unittest.TestCase):
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

if __name__ =='__main__':
    unittest.main()
