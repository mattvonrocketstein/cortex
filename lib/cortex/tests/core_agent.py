""" cortex.tests.core_agent
"""

from unittest import TestCase

from cortex.core.node import Agent
from cortex.core.node import AgentManager

class AgentManagerCheck(TestCase):
    """ tests for the agent manager """

    def test_load_duplicates(self):
        self.assertTrue('dupetest' not in self.universe.agents.as_dict)
        dynclass = Agent.subclass()
        kargs = dict(name='dupetest', kls=dynclass,
                     kls_kargs=dict(universe=self.universe), #TODO make this implied
                     )
        self.universe.agents.load_item(**kargs)

        ## check registry two ways
        self.assertTrue('dupetest' in self.universe.agents.registry)
        self.assertTrue('dupetest' in self.universe.agents)


        hds = self.universe.agents.registry['dupetest']
        obj = hds.obj
        self.assertRaises(AgentManager.Duplicate,
                          lambda: self.universe.agents.load_item(**kargs))
        self.universe.agents.unload(obj)


    def test_agentmanager_load_unload(self):
        self.assertTrue('tmptest' not in self.universe.agents.as_dict)
        dynclass = Agent.subclass()
        kargs = dict(name='tmptest', kls=dynclass,
                     kls_kargs=dict(universe=self.universe), #TODO make this implied
                     )
        self.universe.agents.load_item(**kargs)

        ## check registry two ways
        self.assertTrue('tmptest' in self.universe.agents.registry)
        self.assertTrue('tmptest' in self.universe.agents)


        hds = self.universe.agents.registry['tmptest']
        obj = hds.obj
        self.assertEqual(type(obj), dynclass, "agentmanager registered kls but did not instantiate it")

        ## ensure started
        self.assertTrue(obj.started, "agentmanager built instance but did not start it")

        self.universe.agents.unload(obj)

        ## check registry two ways
        self.assertTrue('tmptest' not in self.universe.agents)
        self.assertTrue('tmptest' not in self.universe.agents.registry)

        ## ensure stopped
        self.assertTrue(not obj.started)
        self.assertTrue(obj.stopped)

    def test_agent_manager(self):
        # is the agentmanager an agentmanager?
        self.assertEqual(type(self.universe.agents), AgentManager)

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
    def test_self_as_service(self):
        # is the unittest service installed as a service?
        self.assertTrue( [ self.__class__.__name__.lower() in self.universe.services ] )

    def test_basic_autonomy(self):
        #test basic autonomy: is the test is running?  then we should be started
        self.assertTrue(self.started)
        self.assertTrue(not self.is_stopped)
        self.assertTrue(not self.stopped)

    def test_autonomy_spec(self,other=None):
        # test autonomy spec
        other = other or self
        F = lambda x: callable(getattr(other,x,None) )
        self.assertTrue(F('iterate'))
        self.assertTrue(F('run'), "{o} has no run method".format(o=other))
        self.assertTrue(F('start'))
        self.assertTrue(F('stop'))

    def test_autonomy_for_every_service(self):
        # every service registered with this universe
        # should use the autonomy mixin, and so should
        # implement the autonomy spec
        for service in self.services.values():
            self.test_autonomy_spec(service)
