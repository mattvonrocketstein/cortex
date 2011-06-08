from unittest import TestCase,main

from cortex.core.agent import Agent
from cortex.core.agent import AgentManager
from cortex.core.util import report
from cortex.tests import wait, X, result_factory
from cortex.core.agent.agentifier import agentifier
class AgentifierTest(TestCase):
    """ tests for the agentifier """

    def test_function(self):
        class X(object):
            pass

        def f():
            print 3
            X.val=1

        #A = Agent.subclass(iterate=f)
        a = agentifier(f)
        a.start()
        a.play()
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        self.assertTrue(getattr(X,'val',0)==1)

    def test_thread(self):
        pass

if __name__=='__main__':
    main()
