from cortex.core.parsing import Nodeconf

class NodeConfAspect(object):
    """ """
    def read_nodeconf(self):
        """ iterator that returns decoded json
            entries from self.nodeconf_file
        """
        nodeconf_err = 'Universe.nodeconf_file tests false or is not set.'
        assert all([hasattr(self, 'nodeconf_file'),
                    self.nodeconf_file]), nodeconf_err
        jsons = Nodeconf(self.nodeconf_file).parse()
        return jsons

    @property
    def Nodes(self):
        """ nodes: static definition """
        blammo = getattr(self, '_use_nodeconf', self.read_nodeconf)
        return blammo() if callable(blammo) else blammo

    @classmethod
    def set_nodes(self, val):
        """ method to overwrite the property above.  might seem weird, but
            the universe is a singleton so it's not really that strange.
            why would you use this?  maybe you're generating it dynamically
            instead of from a file.  or, if you're initializing the universe
            completely via the API, maybe it would be useful afterwards to
            call something like Universe.set_nodes([]) to use a nil config
            w/o saving such a trivial thing to a file.
        """
        self.Nodes = val
