""" cortex.tests.agents_watchdog
"""

from unittest import TestCase

#from cortex.agents.watchdog import WatchDog
from cortex.tests import wait
class WatchdogTest(TestCase):
    """ """
    def asdftest_watchdog_load(self):
        self.universe.agents(WatchDog, 'wdtest')
        err = "agents.load did not work."
        self.assertTrue('wdtest' in self.universe.agents, err)
        err = ""
        #self.assert
