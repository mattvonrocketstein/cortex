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

    def __pow__(self, other):
        return self.agents[other].obj

    def _retrieve_string_from_services(self, name):
        try:
            out = self.services[name]
            return out and out.obj
        except self.services.NotFound:
            return None

    def _retrieve_string_from_agents(self, name):
        try:
            out = self.agents[name]
            return out and out.obj
        except self.agents.NotFound:
            return None

    # TODO: multimethods
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
            result = self._retrieve_string_from_services(other) #or \
                     #self._retrieve_string_from_agents(other)
            if result is None:
                report('no such service/agent', other)
                return None
            else:
                return result
        elif isinstance(other, Service):
            return other.__class__.__name__.lower()
        else:
            raise Exception,'passing objects like that into __or__ is NIY'
