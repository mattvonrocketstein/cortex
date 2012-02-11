""" cortex.core.parsing
"""
import simplejson
from cortex.core.util import report

class Nodeconf:
    """ currently just a json parser that respects comments """

    def __init__(self, nodeconf_file, list=None, raw=None):
        self.nodeconf_file = nodeconf_file
        self.raw = raw
        self.list = list

    def write(self, place):
        """ """
        file=open(place,'w')
        file.write(self.as_string())
        file.close()
        report('finishing writing to ',place)
        return place

    def __repr__(self):
        """ """
        return str( [x for x in self] )

    def as_string(self, one_line=False):
        """
        """
        if self.nodeconf_file:
            nodeconf_file = self.nodeconf_file
            return '\n'.join(open(nodeconf_file).readlines())
        elif self.list:
            return '\n'.join([simplejson.dumps(x) for x in self.list])
        else:
            assert self.raw, "need raw "
            return self.raw
            import types

            if type(self.raw) in types.StringTypes:
                return self.raw
            sep = (one_line and '') or '\n'
            return sep.join([simplejson.dumps(element) for element in self.raw])

    def __iter__(self):
        """ dumb helper """
        if self.list: return self.list
        nodeconf = self.as_string()
        nodeconf = [z.strip() for z in nodeconf.split('\n')]
        return iter(nodeconf)

    def should_parse_line(self, line):
        """ Respect comments and disregard empties.. we won't
            rip these out in the __iter__ helper just
            in case they have semantic value.
        """
        return line and not line.strip().startswith('#')

    def parse(self, ignore=[]):
        """ return a list of legal json items """
        nodes = []
        for line in [x for x in self]:

            # Respect comments and disregard empties
            if not self.should_parse_line(line):
                continue

            #report('got line', line)
            try:
                nodedef = simplejson.loads(line)
            except:
                report("error decoding..", line)
            else:
                #report('encoded..', nodedef)
                nodes.append(nodedef)
        if ignore:
            filtered=[]
            for ignored_instruction in ignore:
                for node in nodes:
                    if not node: continue
                    instruction = node and node[0]
                    if ignored_instruction != instruction:
                        filtered.append(node)
            nodes = filtered
        return nodes
