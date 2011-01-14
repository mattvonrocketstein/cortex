""" cortex.core.tests.manager

"""

import unittest

from cortex.core.manager import Manager

#from cortex.contrib.hds import HDS
from cortex.core.hds import HDS

class ManagerTest(unittest.TestCase,):
    """ test the abstract manager """

    def setUp(self):
        """ """
        self.man = Manager()
    ## Registration and simple stuff
    def test_init(self):
        """ test that initial internal datastores get
            setup somewhat correctly
        """
        self.assertEquals(self.man._pending, [])
        self.assertEquals(self.man.registry, {})
    def test_register_and_retrieve_by_name(self):
        """ see if simple registration even works """
        self.man.register('sherlock', address='221 baker st')

    def test_register_and_dictionary(self):
        addy       = '221 baker st'
        whats_this = self.man.register('sherlock', address=addy)

        # both register and retrieval should return the same thing
        sherlock = self.man.registry['sherlock']
        self.assertEqual(whats_this, sherlock)

        # address should have gone it with the call to .register()
        self.assertTrue(sherlock.address == addy)
        # timestamp should be set
        self.assertTrue('stamp' in sherlock.keys())

        # after a variable is set, it should be in there
        sherlock.x = 1
        self.assertTrue('x' in sherlock.keys())
        self.assertTrue(sherlock.x==1)

    ## Boot order stuff
    def test_bo(self):
        self.man.register('P', one='1')
        self.man.register('Q', two='2')
        print self.man.resolve_boot_order()
if __name__ =='__main__':
    unittest.main()
