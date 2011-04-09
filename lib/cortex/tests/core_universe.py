""" core_universe"""

from unittest import TestCase

from cortex.core.node import Agent

class ServiceManagerCheck(TestCase):
    def test_service_manager(self):
        # is the servicemanager a servicemanager?
        from cortex.core.service import ServiceManager
        services = self.universe.services
        self.assertEqual(type(services), ServiceManager)

        services = self.services
        self.assertTrue('unittestservice' in services)
        self.assertTrue('postoffice' in services)
        self.assertTrue('linda' in services)

    def test_service_load(self):
        #TODO: define and convert this test to use the trivial service
        pass

class AgentManagerCheck(TestCase):
    def test_agentmanager_load(self):
        self.assertTrue('tmptest' not in self.universe.agents.as_dict)
        self.universe.agents.load_item(name='tmptest',
                                       kls=Agent.subclass(),
                                       kls_kargs=dict(universe=self.universe),)
        self.assertTrue('tmptest' in self.universe.agents)
        self.assertTrue('tmptest' in self.universe.agents.registry)

    def test_agent_manager(self):
        # TODO: define and convert this test to use the trivial agent
        # is the agentmanager an agentmanager?
        from cortex.core.node import AgentManager
        agents = self.universe.agents
        self.assertEqual(type(agents), AgentManager)

    def test_agent_manager_flush(self):
        #self.universe.agents.flush()
        #self.assertEqual(len(agents),0)
        pass

        # NOTE: tests False when empty (it's a feature..)
        #self.assertTrue(self.universe.agents)

class UniverseCheck(AgentManagerCheck, ServiceManagerCheck):
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

    def test_reactor_calls(self):
        """ "self.universe.reactor.callLater(1, callback)"
            does not work-- apparently threadpool blocks it.
        """
        class result_holder: switch=0
        def callback(): result_holder.switch += 1
        self.universe.reactor.callFromThread(callback)
        import time;time.sleep(1)
        self.assertEqual(result_holder.switch,1)
