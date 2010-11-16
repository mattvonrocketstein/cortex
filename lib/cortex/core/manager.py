""" cortex.core.manager

      Manager pattern stuff
"""

import datetime

from cortex.core.hds import HierarchicalData
from cortex.core.util import report

class Manager(object):
    """ Managers are inspired by django's managers.  Think of
        this class as a collection of patterns in tracking,
        reporting, and order statistics.  Example usage follows.

          Build an empty manager, or initialize it with some data
            >>> person_manager = Manager()
            >>> person_manager = Manager(**data) # Not implemented yet

          A person as a named collection of attributes:
            >>> jenny_attrs = dict(name='Jenny', phone=8675309, button=lambda x: x)

          Use <Manager> to wrap it
            >>> jenny = person_manager.register('jenny', jenny_attrs)

          Use lazy attributes as implicit data store (these examples are equivalent)
            >>> person_manager['jenny'].random.extra.data = {1:1,2:2,'whatever:''}
            >>> person_manager.jenny.random.extra.data = {1:1,2:2,'whatever:''}
            >>> jenny.random.extra.data = {1:1,2:2,'whatever:''}


         NOTE: if subclasses define 'asset_class', then it will be used in place of
               the default HierarchicalData
    """

    class NotFound(Exception): pass

    def __init__(self, *args, **kargs):
        """ """
        self.registry     = {}

    @property
    def last(self):
        """ all incoming data should be stamped; this function returns the oldest"""
        return self[self.as_list[-1]]

    @property
    def first(self):
        """ all incoming data should be stamped; this function returns the youngest"""
        return self[self.as_list[0]]

    def stamp(self, name):
        """ timestamp element with name <name> """
        self.registry[name].stamp = datetime.datetime.now()

    def register(self, name, **item_metadata):
        """ register object <name> with namespace <item_metadata>
        """
        name = str(name)
        self.registry[name] = getattr(self, 'asset_class', HierarchicalData)()
        for key,value in item_metadata.items():
            setattr( self.registry[name], key, value)
        self.stamp(name)
        report('saving name', name)
        return self[name]

    def __str__(self):
        """ """
        return str( self.as_list )

    def __repr__(self):
        """ """
        return 'manager(' + str(self) + ')'

    def __getitem__(self, name):
        """ retrieve service by name
            Example:

               peers.as_list --> sorted by stamp, returns a list of names
               peers[int]    --> sorted by stamp, returns a HDS-Peer
               peers[str]    --> sorted by stamp, returns a HDS-Peer
               peers[peers[0]] --> returns the most recent HDS-Peer

            NOTE: currently case insensitive!
        """
        if isinstance(name, int):
            return self.registry[self.as_list[name]]
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

    def __iter__(self):
        """ dumb proxy """
        return iter(self.registry)
