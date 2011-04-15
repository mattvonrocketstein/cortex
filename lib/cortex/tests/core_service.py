""" cortex.tests.core_service
"""

from unittest import TestCase
from cortex.core.service import Service, ServiceManager

class ServiceManagerCheck(TestCase):
    """ tests for the service manager """

    def test_service_manager(self):
        # is the servicemanager a servicemanager?
        services = self.universe.services
        self.assertEqual(type(services), ServiceManager)

        services = self.services
        self.assertTrue('unittestservice' in services)
        self.assertTrue('postoffice' in services)
        self.assertTrue('linda' in services)

    def test_service_load(self):
        self.assertTrue('tmptest' not in self.universe.services.as_dict)
        self.universe.services.load_item(name='tmptest',
                                       kls=Service.subclass(),
                                       kls_kargs=dict(universe=self.universe),)
        self.assertTrue('tmptest' in self.universe.services)
        self.assertTrue('tmptest' in self.universe.services.registry)
        self.universe.services.unload('tmptest')
