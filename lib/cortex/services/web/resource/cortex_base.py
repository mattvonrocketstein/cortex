"""
"""
from twisted.web.resource import Resource

class CBR(Resource):
    " Cortex base-resource "

    def render_GET(self, request):
        """ """
        T, ctx = self.get_template_ctx(request)
        return str(template(T).render(**ctx))

    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)
