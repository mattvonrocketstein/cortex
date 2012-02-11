""" cortex.core.notation
"""
import types

from cortex.services import Service
from cortex.core.util import report

class UniverseNotation:
    """ """

    def __xor__(self, other):
        """ syntactic sugar launching another universe with given
            nodeconf file. example usage follows.

               (universe ^ '~cortex/etc/master.conf')
        """


    def __or__(self, other):
        """ syntactic sugar for grabbing a service by name,
            given an actual service, getting it's name. example
            usage follows.

              >>> ( universe | "postoffice" )
              <PostOffice-Service 161820524>
              >>> postoffice =  ( universe | "postoffice" )
              >>> ( universe | postoffice )
              "postoffice"

        """
        if type(other) in types.StringTypes:
            try:
                out = self.services[other]
                return out and out.obj
            except self.services.NotFound:
                report('no such service found', other)
                return None
        elif isinstance(other, Service):
            return other.__class__.__name__.lower()
        else:
            raise Exception,'passing objects like that into __or__ is NIY'
