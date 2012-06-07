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

class Root(CBR):
    def __init__(self, favicon=None, static=None):
        Resource.__init__(self)
        self.putChild('static',      _static.File(static))
        self.putChild('favicon.ico', _static.File(favicon))
        self.putChild('main_nav',     NavResource())


    def get_template_ctx(self, request):
        """ """
        children = self.children.copy()
        return ('root',
                dict(children=children,
                     contents=dir(self)))

class NavResource(CBR):

    isLeaf = True

    @property
    def _children(self):
        return 'universe _code web'.split()

    def get_template_ctx(self, request):
        return ('nav', dict(children=self._children,))
