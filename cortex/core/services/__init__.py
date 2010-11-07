""" cortex.core.__init__

    TODO: stub out this one
       def django_service(self):
           import django.core.handlers.wsgi
           application = django.core.handlers.wsgi.WSGIHandler()

"""


from cortex.core.node import Node
from cortex.core.util import report
from cortex.core.restrictions import __domain_restricted__

import datetime
class Manager(object):
    class NotFound(Exception): pass
    def __str__(self):
        return str(self.as_list)
    def __repr__(self):
        return 'peer-manager('+str(self)+')'
    def __getitem__(self, name):
        """ retrieve service by name

            NOTE: currently case insensitive!
        """
        if isinstance(name, int):
            return self.as_list[name]
        if isinstance(name, str):
            for nayme in self.registry:
                if name.lower() == nayme.lower():
                    return self.registry[name]
            raise self.NotFound('No such service: ' + name)

    @__domain_restricted__
    def register(self, auth, _rsrc):
        """ registers resource <_rsrc> on <auth>'s authority.

              NotImplementedYet
        """
        self.registry[auth] = _rsrc
        #report('registering resource', _rsrc)

    @property
    def as_list(self):
        out = [ x for x in self ]
        out.sort(lambda x, y: cmp(self.registry[x].stamp,
                                 self.registry[y].stamp))
        return out

    aslist=as_list

    def __init__(self):
        """ """
        self.registry     = {}

    def __iter__(self):
        """ dumb proxy """
        return iter(self.registry)
from cortex.core.hds import HierarchicalData
class PeerManager(Manager):
    """ """
    def register(self, name, **kargs):
        """ """
        name = str(name)
        self.registry[name] = HierarchicalData()
        for key,value in kargs.items():
            setattr(self.registry[name], key, value)
        #report('registering', str(kargs))
        self.stamp(name)

    def stamp(self,name):
        """ """
        self.registry[name].stamp = datetime.datetime.now()

    def __iter__(self):
        """ dumb proxy """
        return Manager.__iter__(self)



class ServiceManager(Manager):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """

    def __init__(self, service_list):
        """ """
        Manager.__init__(self)
        self.service_list = service_list

    def stop_all(self):
        """ """
        [ s.stop() for s in self ]

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
