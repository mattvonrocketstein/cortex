""" cortex.services.linda """

import re, pickle
import datetime
from socket import socket

from cortex.core.util import report, console
from cortex.services import Service
from cortex.core.atoms import PersistenceMixin

from twisted.internet import protocol
from twisted.internet import reactor

from lindypy.TupleSpace import TSpace
from lindypy.TupleSpace import Client,tuplespace

class Memory(TSpace,PersistenceMixin):
    """
         A thin wrapper around lindypy's tuplespace.
    """
    def __init__(self, owner,name=None, filename=None):
        """ """
        self.owner = owner
        self.name  = name or (str(owner) + ' :: ' + str(id(owner)))
        self.filename = filename or self.owner.universe.tmpfile().name
        TSpace.__init__(self)

        # Sign it.
        self.add(('__name__',  self.name))
        self.add(('__stamp__', str(datetime.datetime.now())))

    #def __getattr__(self,name):
    #    return print 'mem: getattr fail', name

    def shutdown(self):
        """ TODO: proxy to TSpace shutdown? """
        report("Shutting down Memory.")

    def serialize(self):
        """ """
        _str = pickle.dumps(self.values())
        return _str

    def save(self):
        """ """
        report('persisting memory to', self.filename)
        PersistenceMixin.save(self.filename)
        report('persisted memory to', self.filename)

    def get_many(self, pattern):
        """ """
        out=[]
        while True:
            try:
                out.append(self.get(pattern,remove=True))
            except KeyError:
                break
        return out

    def values(self):
        """ """
        #print 'valued'
        return TSpace.values(self)

    def get(self, *args, **kargs):
        """ """
        #print 'get', args, kargs
        return TSpace.get(self, *args, **kargs)

    def add(self, *args, **kargs):
        """ """
        #print 'added', args, kargs
        return TSpace.add(self, *args, **kargs)

class Linda(Service):
    """ Linda Service:
          start:
          stop:
    """

    def _post_init(self):
        """ """
        self.universe.ground = Memory(self)


    def watch(self):
        """ """
        #report('hello')
        self.universe.reactor.callLater(1, self.watch)

    def start(self, universe=True):
        """ """
        report("Starting linda tuplespace")
        self.universe.reactor.callLater(1, self.watch)

    def stop(self):
        """ """
        super(Linda,self).stop()
        self.universe.ground.shutdown()
