from twisted.web.resource import Resource
from cortex.services.web.template import template
class Root(Resource):
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
