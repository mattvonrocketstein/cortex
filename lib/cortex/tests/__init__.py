""" tests for cortex
"""
import time

import uuid

def uniq():
    return str(uuid.uuid1()).split('-')[0]

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
