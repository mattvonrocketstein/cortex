""" cortex.services.unittesting
"""

import unittest
from unittest import TestCase
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
        """
        #nose.core.runmodule(name='__main__', **kw)
        #def suite(dct):
        #    UtestClass = type('D',(TestCase,), dct )
        #    return unittest.TestSuite(map(UtestClass, dct.keys()))

        #def asuite():
        #    tests = ['test_default_size', 'test_resize']
        #    return unittest.TestSuite(map(WidgetTestCase, tests))
        #x = suite(namespace).run(unittest.TestResult())
        #suite(tests).run()
        """
        namespace = self.get_all_tests()
        tests = namespace.keys()
        report("Found {N} tests".format(N=len(tests)))
        tests = self.get_all_tests().items()
        for name, test in tests:
            report("testing",name)
            yield test()
        report("Finished Tests")

class ChannelCheck(TestCase):
    def test_channels(self):
        class result_holder: switch=0
        def callback(*args, **kargs): result_holder.switch = 1

        # grab postoffice service handle from universe
        poffice = (self.universe|'postoffice')

        # ensure the events channel has already been registered with postoffice
        chans = poffice.enumerate_embedded_channels()
        chan_names = [ chan._label for chan in chans ]
        self.assertTrue('EVENT_T' in chan_names)

        # create a subchannel, make sure we can see it
        chan_sandwich = poffice.event.sandwich
        self.assertTrue(poffice.event.subchannels(),[chan_sandwich])

        # test subscriptions
        # (block for a second so callback gets hit)
        chan_sandwich.subscribe(callback)
        chan_sandwich("test")
        import time; time.sleep(1)
        if result_holder.switch == 0:
            self.assertTrue(False and "callback not fired :(" )

        # test that destroy unsubscribes and unregisters
        chan_sandwich.destroy()
        self.assertTrue(len(poffice.event.subchannels())==0)

class UniverseCheck(TestCase):

    def test_universe(self):
        "is the universe setup? "
        self.assertTrue(self.universe)

    def test_reactor(self):
        "is the reactor setup? "
        self.assertTrue(self.universe.reactor)

    def test_services(self):
        " is the servicemanager a servicemanager? "
        from cortex.core.service import ServiceManager
        services = self.universe.services
        self.assertEqual(type(services), ServiceManager)

        services = self.services
        self.assertTrue('sanitycheck' in services)
        self.assertTrue('postoffice' in services)
        self.assertTrue('linda' in services)

class AgentCheck(TestCase):

    def test_autonomy(self):
        "test basic autonomy: is the test is running, we should be started"
        self.assertTrue(self.started)
        self.assertTrue(not self.is_stopped)
        self.assertTrue(not self.stopped)

    def test_autonomy2(self,other=None):
        "test autonomy spec"
        other = other or self
        F = lambda x: callable(getattr(other,x,None) )
        self.assertTrue(F('iterate'))
        self.assertTrue(F('run'), "{o} has no run method".format(o=other))
        self.assertTrue(F('start'))
        self.assertTrue(F('stop'))
    def test_autonomy_for_every_service(self):
        for service in self.services.values():
            self.test_autonomy2(service)

class TestTools:
    @property
    def services(self):
        """ proxy for convenience """
        return self.universe.services.as_dict

class SanityCheck(unittestservice, TestTools,AgentCheck, UniverseCheck, ChannelCheck):
    _testMethodName = 'xxx'


    def test_service_load_unloading(self):
        """ """
        class SimpleService(Service):
            pass

    def test_self_as_service(self):
        " is the unittest service installed as a service? "
        self.assertTrue( [ self.__class__.__name__.lower() in self.universe.services ] )

    def test_reactor_calllaters(self):
        pass
