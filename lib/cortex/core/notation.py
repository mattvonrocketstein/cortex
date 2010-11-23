""" cortex.core.notation
"""

import os

class UniverseNotation:
    """ """
    def __xor__(self, other):
        """ syntactic sugar launching another universe with given
            nodeconf file. example usage follows.

               (universe ^ '~cortex/etc/master.conf')
        """
        new_command_line_invocation = self.system_shell + '"' + self.command_line_prog + ' --conf='+other + '"&'
        os.system(new_command_line_invocation)

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
        import types
        if type(other) in types.StringTypes:
            try:
                out = self.services[other]
                return out and out.service_obj
            except self.services.NotFound:
                report('no such service found', other)
                return None
        elif isinstance(other, Service):
            return other.__class__.__name__.lower()
        else:
            raise Exception,'passing objects like that into __or__ is NIY'
