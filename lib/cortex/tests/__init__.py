""" tests for cortex
"""
import time
from cortex.core.util import uniq

def wait():
    """ normally this would be obnoxious in unittests,
        but since it would be simple to make every testcase
        class to run concurrently, it's not a big deal.
    """
    time.sleep(1)

class X(Exception):
    """ an exception that is sometimes
        raised intentionally inside the
        utests
    """
    pass

def result_factory():
    holder = type('result_holder',tuple(),dict(switch=0))
    incrementer = lambda: setattr(holder, 'switch',
                                  holder.switch + 1)
    return holder, incrementer

def get_bases():
    """ TODO: discover these so the list doesn't have to be touched..
    """
    ## Test-classes to use
    from cortex.tests.core_metaclasses import MetaclassesTest
    from cortex.tests.core_universe import UniverseCheck
    from cortex.tests.core_channels import ChannelCheck
    from cortex.tests.core_agent import AgentCheck
    from cortex.tests.agents_watchdog import WatchdogTest
    bases = (MetaclassesTest, AgentCheck,
             WatchdogTest,    UniverseCheck,
             ChannelCheck, )
    test_args   = dict(bases=bases)

    return test_args

from cortex.core.data import _standardsession
class testsession(_standardsession):
    def __init__(self):
        super(testsession,self).__init__()
        self.set_interactive(False)
        from cortex.tests import get_bases
        from cortex.services.unittesting import UnitTestService
        self.add_instruction([ "load_service", ("unittestservice",),    get_bases()  ])
        #self.end_when_finished_with_tests()

    def end_when_finished_with_tests(self):
        # Specify terminating conditions to declare as goals
        from cortex.core.util import service_is_stopped
        from cortex.core import api
        tests_are_finished_running = service_is_stopped('UnitTestService')
        api.declare_goals( [ tests_are_finished_running ] )

    def start(self):
        from cortex.core import api
        api.do( self.instructions )
        api.universe.play()

def main():
    from cortex.tests import testsession
    session = testsession()
    session.start()
