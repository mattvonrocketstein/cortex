""" cortex.mixins.mobility
"""

class MobileCodeMixin(object):
    """ """
    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]
