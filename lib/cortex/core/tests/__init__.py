""" cortex.core.tests
"""
"""
import sys
import unittest, __builtin__

from cortex.core import api
from cortex.services import terminal
from cortex.core.node import Agent
from cortex.core.common import AgentPrerequisiteNotMet


#from reimport import *
#reimport(api)
#reimport(terminal)
class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}


"""

import unittest

class GroundTest(unittest.TestCase):
     #test the main cortex data-store

    def setUp(self):
        pass

    def _import(self, name, *args, **kargs):
        #def _import(self, name, globals=None, locals=None, fromlist=[],**kargs):
        #result = apply(self.realImport, (name, globals, locals, fromlist, ))
        print '-'*80,(name, args, kargs)
        result = self.realImport(name, *args, **kargs)
        self.newModules[name] = 1
        return result

    def uninstall(self):
        for modname in self.newModules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                del(sys.modules[modname])
        __builtin__.__import__ = self.realImport

class AgentManagerTest(unittest.TestCase):
    """ test the main cortex data-store """
    def tearDown(self):
        self.rollbackImporter.uninstall()

    def setUp(self):
        """ """
        self.rollbackImporter = RollbackImporter()

        class TerminalExample(Agent):
            requires_services = ['terminal']
            def ampersand_processor(self, source, *args, **kargs):
                """ A new input processor for the terminal..
                """
                print "BLAMMO"

            def setup(self):
                """ """
                terminal = (self.universe|'terminal')
                comment_predicate = lambda source: source.strip().startswith('&')
                terminal.attach_proc(self.ampersand_processor, comment_predicate)
        self.TerminalExample = TerminalExample
        self._setup_params()

    def _setup_params(self):
        """ Parameters for the services. mostly empty and ready to override """

        # Cortex-Terminal arguments: be quiet
        self.term_args  = {'syndicate_events_to_terminal' : False}
        # Arguments for the API-serving daemon
        self.api_args   = {}
        # Linda (tuplespace) parameters
        self.linda_args = {}
        # Network-mapper parameters
        self.map_args   = {}
        # Postoffice parameters
        self.post_args  = {}

        self.chat_args  = dict(kls=self.TerminalExample)

    def test_honors_requires_services2(self):
        """ """
        # This breaks because the terminal-service isn't loaded,
        #  and our Agent names it as a requirement.
        api.do( [
                   [ "load_service", ("api",),            self.api_args   ],
                   [ "load_service", ("_linda",),         self.linda_args ],
                   [ "load_service", ("terminal",),       self.term_args  ],
                   [ "load_service", ("postoffice",),     self.post_args  ],
                   [ "load_service", ("network_mapper",), self.map_args   ],
                   [ "build_agent",  ('test-agent',),     self.chat_args  ],
                   ])

        # Invoke the universe (mainloop)
        try:
            api.universe.play()
        except AgentPrerequisiteNotMet:
            self.fail('should have thrown AgentPrerequisiteNotMet')

    def test_honors_requires_services(self):
        """ """
        # This breaks because the terminal-service isn't loaded,
        #  and our Agent names it as a requirement.
        api.do( [
                   [ "load_service", ("api",),            self.api_args   ],
                   [ "load_service", ("_linda",),         self.linda_args ],
                   [ "load_service", ("postoffice",),     self.post_args  ],
                   [ "load_service", ("network_mapper",), self.map_args   ],
                   [ "build_agent",  ('test-agent',),     self.chat_args  ],
                   ])

        # Invoke the universe (mainloop)
        try:
            api.universe.play()
        except AgentPrerequisiteNotMet:
            print '-----'
        else:
            self.fail('should have thrown AgentPrerequisiteNotMet')

class GroundTest(unittest.TestCase):
    """ test the main cortex data-store """




class UniverseTest(unittest.TestCase):
     #test the universe

    def setUp(self):
        pass


class NodeTest(unittest.TestCase):
     pass #test the node

class AgentTest(unittest.TestCase):
    """ test the node  """


    def setUp(self):
        pass

if __name__ =='__main__':
    unittest.main()
