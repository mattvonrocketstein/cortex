""" cortex.services.web.resource.root
"""

from twisted.web.resource import Resource

from twisted.web import static as _static
from cortex.services.web.template import template

class CBR(Resource):
    " Cortex base-resource "

    def render_GET(self, request):
        """ """
        T, ctx = self.get_template_ctx(request)
        return str(template(T).render(**ctx))

    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

class JSONResource(Resource):
   def render_GET(self, request):
       request.setHeader("content-type", "text/json")
       import simplejson
       return simplejson.dumps(self.render_JSON(request))

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


class Root(CBR):
    def __init__(self, favicon=None, static=None):
        Resource.__init__(self)
        self.putChild('static',      _static.File(static))
        self.putChild('favicon.ico', _static.File(favicon))
        self.putChild('main_nav',    NavResource())


    def get_template_ctx(self, request):
        """ """
        children = self.children.copy()
        return ('root',
                dict(boot_order=self.parent.universe.services._boot_order,
                     command_line_options = self.parent.universe.command_line_options._getLeaves(),
                     children=children,
                     contents=dir(self)))

class NavResource(CBR):

    isLeaf = True

    @property
    def _children(self):
        return 'universe web conf _code '.split()

    def get_template_ctx(self, request):
        return ('nav', dict(children=self._children,))
