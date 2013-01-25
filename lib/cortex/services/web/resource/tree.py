""" cortex.services.web.resource.tree
"""

from .json import JSONResource

class TreeResource(JSONResource):
    """ TODO move this """
    def __init__(self, universe):
        self.universe = universe

    def render_JSON(self, request):
        """ by default universe.tree is a nx-style
            edge-list.  convert it here into
            something that d3.js can use
        """
        edge_list = self.universe.tree
        out = []
        for (p, c, d) in edge_list:
            out.append(dict(source=p,target=c,type="notset"))
        return out
