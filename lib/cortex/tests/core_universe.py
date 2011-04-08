""" core_universe"""

from unittest import TestCase

class UniverseCheck(TestCase):
    """ check various aspects of an engaged universe
        for correctness. assumes universe is integrated
        with twisted reactor
    """
    def test_universe(self):
        "is the universe setup? "
        self.assertTrue(self.universe)

    def test_reactor(self):
        "is the twisted reactor installed in the universe? "
        self.assertTrue(self.universe.reactor)

    def test_services(self):
        " is the servicemanager a servicemanager? "
        from cortex.core.service import ServiceManager
        services = self.universe.services
        self.assertEqual(type(services), ServiceManager)

        services = self.services
        self.assertTrue('unittestservice' in services)
        self.assertTrue('postoffice' in services)
        self.assertTrue('linda' in services)

    def test_reactor_calls(self):
        """ "self.universe.reactor.callLater(1, callback)"
            does not work-- apparently threadpool blocks it.
        """
        class result_holder: switch=0
        def callback(): result_holder.switch += 1
        self.universe.reactor.callFromThread(callback)
        import time;time.sleep(1)
        self.assertEqual(result_holder.switch,1)
