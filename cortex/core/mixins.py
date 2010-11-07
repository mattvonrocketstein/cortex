""" cortex.core.mixins
"""

class EventMixin(object):
    """ Can be used on anything with a tuplespace named <ground>
    """
    BASE_NOTICE_TOKEN = 'system_event'
    def push_events(self, *args):
        """ """
        [self.push_event(arg) for arg in args]

    def push_event(self,notice):
        """ """
        self.ground.add( (EventMixin.BASE_NOTICE_TOKEN, notice) )

    @property
    def events(self):
        """ NOTE: currently get_many is destructive by default.
        """
        return self.ground.get_many( (EventMixin.BASE_NOTICE_TOKEN, object) )
