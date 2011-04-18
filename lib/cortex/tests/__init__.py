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
