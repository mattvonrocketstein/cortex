""" cortex.mixins.mobility
"""
LOOPBACK_HOST = '127.0.0.1'
GENERIC_LOCALHOST = 'localhost'

class MobileCodeMixin(object):
    """ """
    @property
    def is_local(self):
        """ """
        return self.host in [LOOPBACK_HOST, GENERIC_LOCALHOST]
