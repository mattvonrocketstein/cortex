"""
"""

from twisted.web.resource import Resource

from twisted.web import static as _static
from cortex.services.web.template import template

class Root(Resource):
    def __init__(self,favicon=None, static=None):
        Resource.__init__(self)
        self.putChild('static',      _static.File(static))
        self.putChild('favicon.ico', _static.File(favicon))
        self.putChild('main_nav',     NavResource(self))

    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        """ """
        children = self.children.copy()
        children.pop('static','')
        children.pop('favicon.ico','')
        ctx = dict(children=children,
                   contents=dir(self))
        return str(template('root').render(**ctx))
class NavResource(Resource):

    isLeaf = True
    def __init__(self, obj):
        self._obj = obj

    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

    def __init__(self,root=None):
        self.root = root

    @property
    def _children(self):
        children = self.root.children.copy()
        children.pop('static','')
        children.pop('favicon.ico','')
        return children

    def render_GET(self,request):
        ctx = dict(children=self._children,)
        return str(template('nav').render(**ctx))
