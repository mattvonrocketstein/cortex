""" cortex.tests.agents_watchdog
"""

from unittest import TestCase

from cortex.tests import wait
from cortex.tests import uniq
from cortex.core.util import report
from cortex.agents.watchdog import WatchDog
from cortex.mixins.flavors import Threadpooler

class WatchdogTest(TestCase):
    """ """

    def test_foo(self):
        x = WatchDog.subclass()
        self.assertTrue(issubclass(x, WatchDog))

    def test_watchdog_load(self):
        def callback():
            raise Exception
            result_holder.switch += 1
        name=uniq()
        A = WatchDog.subclass( success = callback )
        handle = self.universe.agents( A , name=name)
        err = "agents.load did not work."
        self.assertTrue(name in self.universe.agents.keys(), err)
        self.universe.agents.unload(A)
        #self.assertTrue(name not in self.universe.agents.keys(),"unload didn't work")

    def test_watchdog_bark(self):
        name = uniq()
        from cortex.mixins import ReactorRecursion
        class A(WatchDog, ):
            bark = lambda self: report("test")
            watch_list = [lambda: True]
        #A = A<<ReactorRecursion
        self.assertTrue(issubclass(A, WatchDog))
        #
        handle = self.universe.agents( A , name=name)
        self.assertTrue(name in self.universe.agents.keys(),
                        "agents.load did not work.")
        self.assertTrue( handle.started,
                         "agent not started after loading" )
        #[ wait() for x in range(10) ]
        # should see reports firing..
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        self.universe.agents.unload(name)
        self.assertTrue( name not in self.universe.agents.keys(),
                         "unload didn't work" )
