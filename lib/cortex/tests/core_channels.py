""" tests for cortex
    tests.channel
"""
import unittest

from unittest import TestCase

from cortex.tests import wait

class ChannelCheck(TestCase):
    """ test the channel abstraction """

    def test_channels(self):
        class result_holder: switch=0
        def callback(*args, **kargs): result_holder.switch = 1

        # grab postoffice service handle from universe
        poffice = (self.universe|'postoffice')

        # ensure the events channel has already been registered with postoffice
        chans = poffice.enumerate_embedded_channels()
        chan_names = [ chan._label for chan in chans ]
        self.assertTrue('EVENT_T' in chan_names)

        # create a subchannel, make sure we can see it
        chan_sandwich = poffice.event.sandwich
        self.assertTrue(poffice.event.subchannels(),[chan_sandwich])

        # test subscriptions
        # (block for a second so callback gets hit)
        chan_sandwich.subscribe(callback)
        chan_sandwich("test")
        #wait()
        if result_holder.switch == 0:
            self.assertTrue(False and "callback not fired :(" )

        # test that destroy unsubscribes and unregisters
        chan_sandwich.destroy()
        self.assertEqual(len(poffice.event.subchannels()), 0)
