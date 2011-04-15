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
        dct = dict([ [name, getattr(self, name)] for name in names ])
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



        TTR = TextTestRunner(verbosity=2)
        #test_suite = unittest.TestSuite(test_cases)
        #TTR.run(test_suite)
        result = TestResult()
        #yield test_suite.run(result)
        for tc in test_cases:
            #console.draw_line()
            test_suite = unittest.TestSuite([tc])
            TTR.run(test_suite)

            x = test_suite.run(result)
            #if x.failures or x.errors:
            #    report(x,)
            #    break
            #unittest.main()
            yield
        msg = 'Test Results: {E} errors, {F} failures.'
        msg = msg.format(E=len(result.errors),F=len(result.failures))

        print; print console.red(msg)
        show_fails(result)

        print; print console.red(msg)
        show_errors(result)
        yield
    @property
    def services(self):
        """ proxy for convenience """
        return self.universe.services.as_dict
    def _post_init(self, bases):
        """ """
        report("Look ma, I rewrote my bases")
        self.__class__.__bases__ += bases

    def test_service_load_unloading(self):
        """ """
        class SimpleService(Service):
            pass



    _testMethodName = 'WhyDoesThisNeedToBeHere?'
