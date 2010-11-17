""" cortex.core.service
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.util import report, console

class ServiceManager(Manager):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """
    def stop_all(self):
        """ """
        [ s.stop() for s in self ]


class Service(Node):
    """
    """
    def __init__(self, *args, **kargs):
        """ """
        if 'name' in kargs:
            raise Exception,'services specify their own names'
        else:
            kargs.update( { 'name' : self.__class__.__name__ } )
        super(Service,self).__init__(*args, **kargs)

    def _post_init(self):
        """ """
        self.is_stopped = False

    def stop(self):
        """ """
        report("service::stopping")
        self.is_stopped = True
        self.started    = False
        super(Service,self).stop()

    def play(self):
        """
            Convention: services *must* define start() and stop(), therefore
                        the functionality of <play> is implied.
        """
        self.universe.reactor.callLater(1, self.start)
        return self
