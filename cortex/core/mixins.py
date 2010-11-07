""" cortex.core.mixins
"""

NOTICE_T = 'system_notice'

class EventMixin(object):
    """ """
    def push_events(self, string_type, *args):
        """ """
        return [self.push_event(string_type, arg) for arg in args]

    def push_event(self, type_string, notice):
        """ """
        return self.ground.add( (type_string, notice) )

    def events(self,string_type):
        """ """
        out = self.ground.get_many( (string_type, object) )
        out = [x[1:] for x in out] # clean up by chopping off the token
        return out


class NoticeMixin(EventMixin):
    """"""
    def push_notice(self, notice):
        """ """
        return self.push_event(NOTICE_T, notice)

    @property
    def notices(self):
        """ """
        return self.events(NOTICE_T)
