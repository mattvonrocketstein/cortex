""" cortex.services.stub

      a template service. does nothing, but useful to copy
"""
#import multiprocessing
#from multiprocessing import Process, Value, Array

from cortex.core.util import report
from cortex.services import Service


class Stub(Service):
    """ Stub Service:
        start: brief description of service start-up here
        stop:  brief description service shutdown here
    """


    def print_error(self, *errors):
        """ """
        for x in errors:
            pass # choose any errors to ignore and remove them
        report('error_handler for name resolution',str(errors) )

    def stop(self):
        """ """
        Service.stop(self)
        report('Custom stop for', self)

    def start(self):
        """ start is a function, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """
        Service.start(self)

    def iterate(self):
        """ placeholder for an probably atomic action.  this name is used by
            convention ie if <start> invokes it in a while-loop
        """

    def play(self):
        """ stubbed out although services should override
            usually override "start" and not "play" """
        return Service.play(self)
