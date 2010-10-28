""" cortex.core.__init__
"""

from cortex.core.node import Node

class ServiceManager(object):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """
    class NotFound(Exception): pass

    def __init__(self, service_list):
        self.service_list = service_list

    def __getitem__(self, name):
        """ retrieve service by name """
        if isinstance(name, int):
            return self.service_list[name]
        if isinstance(name, str):
            for service in self.service_list:
                if service.name == name:
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
            kargs.update({'name':self.__class__.__name__})
        super(Service,self).__init__(*args, **kargs)
