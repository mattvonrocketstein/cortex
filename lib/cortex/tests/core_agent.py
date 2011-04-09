""" cortex.tests.core_agent
"""

from unittest import TestCase

class AgentCheck(TestCase):
    """ check various aspects of a running agent """

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
