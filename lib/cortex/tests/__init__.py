""" tests for cortex
"""
import time

def wait():
    """ normally this would be obnoxious in unittests,
        but since it would be simple to make every testcase
        class to run concurrently, it's not a big deal.
    """
    time.sleep(1)
