""" cortex.tests.agents_watchdog
"""

from unittest import TestCase

from cortex.tests import wait
from cortex.tests import uniq

from cortex.agents.watchdog import WatchDog

class WatchdogTest(TestCase):
    """ """

    def test_foo(self):
        x = WatchDog.subclass()
        self.assertTrue(issubclass(x, WatchDog))

    def test_watchdog_load(self):
        class xxx(WatchDog.subclass()):
            watch_list = [lambda: True]
            def bark(self):
                raise Exception
        #xxx().bark()
        name = uniq()
        self.universe.agents(xxx, name)
        return

        class result_holder: switch=0
        def callback():
            raise Exception
            result_holder.switch += 1
        #self.universe.agents(WatchDog, 'wdtest', success=callback)
        #err = "agents.load did not work."
        #self.assertTrue('wdtest' in self.universe.agents, err)
        #self.assertTrue(
        #import time;time.sleep(1)
        #self.assertEqual(result_holder.switch, 1)

        #self.
