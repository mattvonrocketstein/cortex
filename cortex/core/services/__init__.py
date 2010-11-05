""" cortex.core.__init__
"""

from cortex.core.node import Node
from cortex.core.util import report
from cortex.core.restrictions import __domain_restricted__

class ServiceManager(object):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """
    class NotFound(Exception): pass

    @__domain_restricted__
    def register(self, auth, _rsrc):
        """ registers resource <_rsrc> on <auth>'s authority.
        """
        self.registry[auth] = _rsrc
        report('registering resource', _rsrc)

    def __init__(self, service_list):
        self.service_list = service_list
        self.registry     = {}

    def __getitem__(self, name):
        """ retrieve service by name

            NOTE: currently case insensitive!
        """
        if isinstance(name, int):
            return self.service_list[name]
        if isinstance(name, str):
            for service in self.service_list:
                if service.name.lower() == name.lower():
                    return service
            raise self.NotFound('No such service: ' + name)

    def __iter__(self):
        """ dumb proxy """
        return iter(self.service_list)

class Service(Node):
    """
    """
    def __init__(self, *args, **kargs):
        if 'name' in kargs:
            raise Exception,'services specify their own names'
        else:
            kargs.update( { 'name' : self.__class__.__name__ } )
        super(Service,self).__init__(*args, **kargs)

    def stop(self):
        """
        """
        report("stopping")
        self.is_stopped = True

    def play(self):
        """
            CONVENTION: services *must* define start() and stop(), therefore
                        the functionality of <play> is implied.
        """
        self.universe.reactor.callLater(1, self.start)
        return self
