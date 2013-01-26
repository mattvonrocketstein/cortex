""" cortex.services.web.resource.redirect
"""

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

class Redirect(Resource):
    def render_GET(self, request):
        return redirectTo(self.url, request)
