""" cortex.core.manager

      Manager pattern stuff
"""

import datetime
from cortex.core.hds import HierarchicalData

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
        self.registry     = {}

    def __iter__(self):
        """ dumb proxy """
        return iter(self.registry)
