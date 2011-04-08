""" cortex.services.unittesting
"""
import unittest
from unittest import TestCase, TestResult, TextTestRunner
from cortex.core.service import Service
from cortex.core.atoms import Threadpooler
from cortex.core.util import report, console
from cortex.core.metaclasses import subclass_tracker

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
        test_suite = unittest.TestSuite(test_cases)
        TextTestRunner(verbosity=2).run(test_suite)
        test_suite.run(TestResult()) #unittest.main()
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

    def test_self_as_service(self):
        " is the unittest service installed as a service? "
        self.assertTrue( [ self.__class__.__name__.lower() in self.universe.services ] )



    _testMethodName = 'WhyDoesThisNeedToBeHere?'
