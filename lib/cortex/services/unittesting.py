""" cortex.services.unittesting
"""
#import unittest2
import unittest
from unittest import TestCase
import nose
from cortex.core.service import Service
from cortex.core.atoms import Threadpooler
from cortex.core.util import report, console

class unittestservice(Threadpooler, Service, TestCase):
    """ """

    def get_all_tests(self):
        names = [x for x in dir(self.__class__) if x.startswith('test_')]
        dct = dict([ [name, getattr(self, name)] for name in names ])
        return dct

    def iterate(self):
        #nose.core.runmodule(name='__main__', **kw)
        #def suite(dct):
        #    UtestClass = type('D',(TestCase,), dct )
        #    return unittest.TestSuite(map(UtestClass, dct.keys()))

        #def asuite():
        #    tests = ['test_default_size', 'test_resize']
        #    return unittest.TestSuite(map(WidgetTestCase, tests))
        namespace = self.get_all_tests()
        #x = suite(namespace).run(unittest.TestResult())
        tests = namespace.keys()
        report("Found {N} tests".format(N=len(tests)))
        #suite(tests).run()
        tests = self.get_all_tests().items()

        for name, test in tests:
            report("testing",name)
            yield test()
        report("Finished Tests")

class SanityCheck(unittestservice, TestCase):
    def test_postoffice(self):
        print (self.universe|'postoffice')
    def test_universe(self):
        "is the universe setup? "
        self.assertTrue(self.universe)

    def test_reactor(self):
        "is the reactor setup? "
        self.assertTrue(self.universe.reactor)

    def test_services(self):
        " is the servicemanager a servicemanager? "
        from cortex.core.service import ServiceManager
        self.assertEqual(type(self.universe.services), ServiceManager)

    def test_service_load_unloading(self):
        """ """
        class SimpleService(Service):
            pass

    def test_self_as_service(self):
        " is the unittest service installed as a service? "
        self.assertTrue( [ self.__class__.__name__.lower() in self.universe.services ] )

    def test_reactor_calllaters(self):
        pass
