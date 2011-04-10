""" cortex.tests.agents_watchdog
"""

from unittest import TestCase

from cortex.tests import wait
from cortex.agents.watchdog import WatchDog

class WatchdogTest(TestCase):
    """ """
    def test_watchdog_load(self):
        self.universe.agents(WatchDog, 'wdtest')
        err = "agents.load did not work."
        self.assertTrue('wdtest' in self.universe.agents, err)
        err = ""
        #self.assert
