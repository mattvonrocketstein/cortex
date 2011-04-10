""" cortex.tests.agents_watchdog
"""

from unittest import TestCase

from cortex.agents.watchdog import WatchDog
from cortex.tests import wait
class WatchdogTest(TestCase):
    """ """
    def test_watchdog_load(self):
        self.assertTrue('wdtest' not in self.universe.agents.as_dict)
        self.universe.agents.load_item(name='wdtest',
                                       kls=WatchDog,
                                       kls_kargs=dict(universe=self.universe),
                                       index=None)
        self.assertTrue('wdtest' in self.universe.agents,
                        "agents.load did not work.")
