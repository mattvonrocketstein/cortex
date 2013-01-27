""" cortex.service
"""
from collections import defaultdict

from cortex.core.util import report, console
from cortex.core.data import NOOP
from cortex.contrib.aima import csp
from cortex.core.agent import Agent, AgentManager
from cortex.core.manager import Manager

from .manager import ServiceManager

class Service(Agent):
    """ Abstractions representing a cortex service
    """
    class ServiceError(Exception):
        """ Move along, nothing to see here """

    def _raise_error(self, msg):
        """ helper for informative exceptions
            TODO: fixme shouldnt this just use fault()
        """
        formatting = dict(msg=msg, service_name=self.__class__.__name__)
        msg = 'Problem with Service@"{service_name}": {msg}'.format(**formatting)
        raise Service.ServiceError(msg)

    def __init__(self, *args, **kargs):
        """ """
        # a list of items that have to be play()'ed before this service
        self._boot_first = []

        if 'name' in kargs:
            self._raise_error('Services specify their own names!')
        else:
            kargs.update( { 'name' : self.__class__.__name__ } )

        super(Service,self).__init__(*args, **kargs)

    @property
    def status(self):
        """ placeholder """
        return self.is_stopped, self.started

    def __repr__(self):
        """ """
        formatting = dict(_id  = str(id(self)),
                          name = self.__class__.__name__)
        return '<{name}-Service {_id}>'.format(**formatting)

    def stop(self):
        """ Convention:
              <stop> for services differs from your typical
              agent because ?
        """
        super(Service, self).stop()
        if isinstance(self, AgentManager):
            self.stop_all()

    def play(self):
        """
            Convention:
              services *must* define <start> and <stop>,
              therefore the functionality of <play> is implied;
              you should not need to override this method.

        """
        self.universe.reactor.callWhenRunning(self.start)
        return self

# A cheap singleton
SERVICES = ServiceManager()
from .topology import TopologyMixin
from .fecund import FecundService
