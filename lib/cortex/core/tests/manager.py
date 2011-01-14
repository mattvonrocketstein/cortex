""" cortex.core.tests



from cortex.contrib.aima.logic import expr, FolKB
from cortex.contrib.aima.logic import variables, fol_bc_ask,pretty

class GroundTest(unittest.TestCase):
     #test the main cortex data-store

    def setUp(self):
        pass

class UniverseTest(unittest.TestCase):
     #test the universe

    def setUp(self):
        pass

class NodeTest(unittest.TestCase):
     #test the node

    def setUp(self):
        pass
"""

import unittest

from cortex.core.manager import Manager
#from cortex.contrib.hds import HDS
from cortex.core.hds import HDS

class ManagerTest(unittest.TestCase):
    """ test the abstract manager """

    def setUp(self):
        self.man = Manager()

    def test_init(self):
        """ """
        self.assertEquals(self.man._pending, [])
        self.assertEquals(self.man.registry, {})
    def test_register_and_retrieve_by_name(self):
        """ """
        self.man.register('sherlock', address='221 baker st')
        #print self.man.registry['sherlock']
        #.values()[0].items()

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

if __name__ =='__main__':
    unittest.main()
