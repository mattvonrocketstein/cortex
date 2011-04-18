""" cortex.tests.core_agent
"""

from unittest import TestCase

from cortex.core.agent import Agent
from cortex.core.agent import AgentManager
from cortex.core.util import report
from cortex.tests import wait, X, result_factory

class AgentManagerCheck(TestCase):
    """ tests for the agent manager """
    def test_mod_op(self):
        # test that the mod operator can partition the agents
        Junk = Agent.subclass(name='throw-away-subclass')
        handle = self.universe.agents(Junk)
        partition = self.universe.agents%Junk
        self.assertEqual(1, len(partition))
        self.assertEqual([handle], partition.values())
        self.universe.agents.unload(partition.values()[0])
        self.assertEqual(0,len(self.universe.agents%Junk))

    def test_load_duplicates(self):
        # test that duplicate agents raise errors
        self.assertTrue('dupetest' not in self.universe.agents.as_dict)
        # this next part is implied for test_load_duplicates2

        kargs = dict(universe=self.universe)
        kargs = dict(name='dupetest',
                     kls=Agent.subclass(),
                     kls_kargs=kargs, )
        self.universe.agents.load_item(**kargs)

        ## check registry two ways
        self.assertTrue('dupetest' in self.universe.agents.registry)
        self.assertTrue('dupetest' in self.universe.agents)

        self.assertRaises(AgentManager.Duplicate,
                          lambda: self.universe.agents.load_item(**kargs))
        result = self.universe.agents.unload(self.universe.agents.registry['dupetest'].obj)
        self.assertEqual(result,'dupetest')

    def test_load_duplicates2(self):
        # should be equivalent to test_load_duplicates
        self.assertTrue('dupetest' not in self.universe.agents.as_dict)
        self.universe.agents(Agent.subclass(),name='dupetest')

        ## check registry two ways
        self.assertTrue('dupetest' in self.universe.agents.registry)
        self.assertTrue('dupetest' in self.universe.agents)

        self.universe.agents.unload(self.universe.agents.registry['dupetest'].obj)


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
        agents = self.universe.agents
        self.assertEqual(agents.registry, {})
        agents(Agent.subclass(),name='flush-test')
        self.assertEqual(len(agents), 1, str(agents))
        agents.flush()
        self.assertEqual(len(agents), 0)

        # NOTE: tests False when empty (it's a feature..)
        #self.assertTrue(self.universe.agents)


class AgentIterationCheck(TestCase):
    def test_agents_iterate1(self):
        # test should be equivalent to test_agents_iterate2
        result_holder,incr = result_factory()
        incr.reentrant = True
        A = Agent.subclass().subclass(iterate=incr)
        handle = self.universe.agents(A);
        self.assertEqual(handle.__class__, A)
        self.assertTrue(handle.started)
        self.assertTrue(handle.iterate!=incr)
        self.assertEqual(1, result_holder.switch)
        self.universe.agents.unload(A)

    def test_agents_iterate21(self):
        # test should be equivalent to test_agents_iterate2,
        # except since it is reactor-recursion-concurrency-flavored,
        # it ought to run more than once.

        result_holder, incr = result_factory()
        from cortex.mixins.flavors import ReactorRecursion
        name = 'tai21'
        class A(Agent,ReactorRecursion):
            def iterate(self):
                incr()
            iterate.reentrant = 1
        #A = (Agent>>ReactorRecursion).subclass(iterate=incr,
        #                                       _iteration_period = .2)
        self.assertTrue(issubclass(A, ReactorRecursion))
        self.assertTrue(issubclass(A, Agent))
        handle = self.universe.agents(A,name=name);
        #wait()
        wait()
        err = "result-holder value is "+str(result_holder.switch)
        self.assertTrue(1 <= result_holder.switch, err+', should be at least one!')
        self.assertTrue(1 < result_holder.switch, err+', should be greater than one (because this is not the trivial agent')
        results = self.universe.agents.unload(A)
        self.assertEqual(results, [name])
        self.assertTrue(A.name not in self.universe.agents)

    def test_agents_iterate2(self):
        # test should be equivalent to test_agents_iterate1
        result_holder, incr = result_factory()
        A = Agent.subclass(name='i2', iterate=lambda self:setattr(result_holder,'switch',1) )
        self.universe.agents(A);
        wait() # give it a change to run a few times even though it shouldnt
        self.assertEqual(1, result_holder.switch)
        self.universe.agents.unload(A)

    def test_agents_iterate3(self):
        # test should be equivalent to test_agents_iterate1
        result_holder, incr = result_factory()
        x = (self.universe|'postoffice').event.i3
        def callback(*args,**kargs): result_holder.switch += 1
        x.subscribe(callback)
        myiterate = lambda : x('arbitrary channel message')
        A = Agent.subclass(universe=self.universe, name='i2', iterate = myiterate )
        self.universe.agents(A);
        self.assertEqual(result_holder.switch, 1)
        self.universe.agents.unload(A)
        x.destroy()

    def asdtest_agents_iterate32(self):
        # like 3, only with nontrivial agent
        result_holder, incr = result_factory()
        x = (self.universe|'postoffice').event.i3
        def callback(*args,**kargs): result_holder.switch += 1
        x.subscribe(callback)
        myiterate = lambda : x('arbitrary channel message')
        A = Agent.subclass(universe=self.universe)
        self.universe.agents(A);
        wait()
        self.assertTrue(result_holder.switch > 1)
        self.universe.agents.unload(A)
        x.destroy()

    def asdf_test_Agents_iterate31(self):
        # like 3, only using context manager
        # test should be equivalent to test_agents_iterate1
        result_holder, incr = result_factory()
        x = (self.universe|'postoffice').event.i3
        def callback(*args, **kargs): incr()
        x.subscribe(callback)
        myiterate = lambda : x('arbitrary channel message')
        with Agent.subclass(universe=self.universe,
                            name='i2',
                            iterate = myiterate ) as A:

            #self.universe.agents(A);
            self.assertEqual(result_holder.switch, 1)
            #self.universe.agents.unload(A)
        x.destroy()

class ContextManagerTest(TestCase):
    def test_is_loaded(self):
        A = Agent.subclass(universe=self.universe, name='isloadt')
        with self.universe.agents.running(A) as handle:
            self.assertTrue(self.universe.agents.is_loaded(handle))
        self.assertTrue(not self.universe.agents.isloaded(handle))

    def test_cm(self):
        A = Agent.subclass(universe=self.universe )
        with self.universe.agents.running(A) as handle:
            self.assertTrue(self.universe.agents.is_loaded(handle))
        self.assertEqual(self.universe.agents%A, {})

class AgentCheck(AgentIterationCheck,ContextManagerTest):
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
