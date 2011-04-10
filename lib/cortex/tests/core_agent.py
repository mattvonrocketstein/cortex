""" cortex.tests.core_agent
"""

from unittest import TestCase

from cortex.core.node import Agent

class AgentManagerCheck(TestCase):
    """ tests for the agent manager """
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

class AgentCheck(TestCase):
    """ check various aspects of a running agent

        (in this case, the unittestservice is the agent in question)
    """

    def test_autonomy(self):
        "test basic autonomy: is the test is running, we should be started"
        self.assertTrue(self.started)
        self.assertTrue(not self.is_stopped)
        self.assertTrue(not self.stopped)

    def test_autonomy2(self,other=None):
        """ test autonomy spec """
        other = other or self
        F = lambda x: callable(getattr(other,x,None) )
        self.assertTrue(F('iterate'))
        self.assertTrue(F('run'), "{o} has no run method".format(o=other))
        self.assertTrue(F('start'))
        self.assertTrue(F('stop'))

    def test_autonomy_for_every_service(self):
        """ every service registered with this universe
            should use the autonomy mixin, and so should
            implement the autonomy spec
        """
        for service in self.services.values():
            self.test_autonomy2(service)
