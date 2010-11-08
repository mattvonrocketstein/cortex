""" cortex.core.__init__

    TODO: stub out this one

       def django_service(self):
           import django.core.handlers.wsgi
           application = django.core.handlers.wsgi.WSGIHandler()
"""


from cortex.core.node import Node
from cortex.core.util import report
from cortex.core.restrictions import __domain_restricted__
from cortex.core.hds import HierarchicalData

import datetime
class Manager(object):
    """ """
    class NotFound(Exception): pass

    @property
    def oldest(self):
        return self[self.as_list[-1]]

    @property
    def newest(self):
        return self[self.as_list[0]]

    def stamp(self,name):
        """ """
        self.registry[name].stamp = datetime.datetime.now()
    def register(self, name, **kargs):
        """ """
        name = str(name)
        self.registry[name] = HierarchicalData()
        for key,value in kargs.items():
            setattr(self.registry[name], key, value)
        self.stamp(name)

    def __str__(self):
        """ """
        return str(self.as_list)

    def __repr__(self):
        """ """
        return 'manager('+str(self)+')'

    def __getitem__(self, name):
        """ retrieve service by name
            Example:

               peers.as_list --> sorted by stamp, returns a list of names
               peers[int]    --> sorted by stamp, returns a names
               peers[str]    --> sorted by stamp, returns a HDS-Peer
               peers[peers[0]] --> returns the most recent HDS-Peer

            NOTE: currently case insensitive!


        """
        if isinstance(name, int):
            return self.as_list[name]
        if isinstance(name, str):
            for nayme in self.registry:
                if name.lower() == nayme.lower():
                    return self.registry[name]
            raise self.NotFound('No such service: ' + name)

    @property
    def as_list(self):
        """ """
        out = [ x for x in self ]
        out.sort(lambda x, y: cmp(self.registry[x].stamp,
                                 self.registry[y].stamp))
        return out

    aslist=as_list

    def __init__(self, *args, **kargs):
        """ """
        #raise Exception,[args,kargs]
        #assert not kargs, "NIY"
        #if args and isinstance(args[0], dict):
        #    self.registery = args[0]
        #else:
        self.registry     = {}

    def __iter__(self):
        """ dumb proxy """
        return iter(self.registry)

class PeerManager(Manager):
    """ """

    class Peer(object):
        pass

    def __iter__(self):
        """ dumb proxy """
        return Manager.__iter__(self)



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
