""" cortex.core.agent.comms_mixin
"""
from channel import channel
from channel import is_declared_callback
from cortex.core.util import report, report_if_verbose

class CommsMixin(object):
    """ NB:   this mixin necessarily implies agents know about channels by default
        TODO: distinction between agent+ and agent-lite..
    """
    def _handle_Meta_subscriptions(self):
        """ TODO: check for boot_first.. consistency """
        subscriptions = getattr(self._opts, 'subscriptions', {})
        for chan_name in subscriptions:
            cb_list = subscriptions[chan_name]
            if isinstance(cb_list,basestring):
                cb_list = [cb_list]
            for cb in cb_list:
                cb = getattr(self, cb)
                report_if_verbose('subscribing {0}.{1} to {2}'.format(self.name,
                                                                      str(cb.__name__),
                                                                      chan_name))
                poffice = (self.universe|'postoffice')
                if chan_name not in poffice.keys():
                    report_if_verbose(
                        'Channel "{0}" does not exist in postoffice, creating it'.format(chan_name))
                    new_chan = getattr(channel, chan_name)
                    new_chan.bind(poffice)
                if not poffice.has_subscription(chan_name,cb):
                    poffice.subscribe(chan_name, cb)

    def _handle_embedded_callbacks(self):
        """ """
        cbs = []
        # FIXME: use goulash.Namespace's
        for x in dir(self):
            if not isinstance(getattr(self.__class__, x, None), property) and \
                is_declared_callback(getattr(self, x)):
                    cbs.append(getattr(self, x))
                    report_if_verbose('honoring embedded callback: ', x, getattr(self,x))
        for cb in cbs:
            cb.bootstrap(self)
