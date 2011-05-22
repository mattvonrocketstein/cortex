""" cortex.services.unittesting
"""
import unittest
from unittest import TestCase, TestResult, TextTestRunner
from cortex.core.service import Service

from cortex.core.util import report, console
from cortex.core.metaclasses import subclass_tracker

from cortex.mixins.flavors import Threadpooler
def show_tb(tbstr):
            print console.colortb(tbstr)
            console.draw_line()

def show_fails(result):
            console.draw_line('Failures:')
            for x in result.failures:
                print '\n',console.red(str(x[0]))
                show_tb(x[1])

def show_errors(result):
            console.draw_line('Errors:')
            for x in result.errors:
                print '\n',console.red(str(x[0]))
                show_tb(x[1])

class UnitTestService(subclass_tracker(Threadpooler, Service, TestCase)):
    """ Cortex Service / Agent"""

    def get_all_tests(self):
        """ enumerate every test_* method in this instance's class """
        names = [x for x in dir(self.__class__) if x.startswith('test_')]
        dct   = dict([ [name, getattr(self, name)] for name in names ])
        return dct

    def iterate(self):
        """ TODO: break up into yields by subclass
            TextTestRunner sig: (stream=sys.stderr, descriptions=True, verbosity=1)
        """
        FTC       = unittest.FunctionTestCase
        FTC_kargs = {} # dict(setUp=setUp)
        namespace = self.get_all_tests()
        functions_to_test = namespace.values()
        report("Found {N} tests".format(N=len(functions_to_test)))
        test_cases = [FTC(f, **FTC_kargs) for f in functions_to_test]
        result = TestResult()
        for tc in set(test_cases):
            test_suite = unittest.TestSuite([tc])
            x = test_suite.run(result)
            if x.failures or x.errors:
                 report(x,)
                 if hasattr(self, 'failfast'):
                     break
            console.draw_line()
            yield
        msg = 'Test Results: {E} errors, {F} failures.'
        msg = msg.format(E=len(result.errors), F=len(result.failures))
        if result.failures:
            print; print console.red(msg)
            show_fails(result)
        if result.errors:
            print; print console.red(msg)
            show_errors(result)
        yield

    @property
    def services(self):
        """ proxy for convenience """
        return self.universe.services.as_dict

    def _post_init(self, bases):
        """ """
        report("Rewriting bases to acquire all tests JIT")
        self.__class__.__bases__ += bases

    def test_only_tested_once(self):
        # so basic i think it can live in the test-runner itself..
        error = "this test got run twice.  error with test runner?"
        self.assertTrue(not hasattr(self,'some_unlikely_name'),error)
        setattr(self,'some_unlikely_name',1)


    _testMethodName = 'WhyDoesThisNeedToBeHere?'
