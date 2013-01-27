""" cortex.services.web.resource.redirect
"""

from twisted.web.resource import Resource
from twisted.web.util import redirectTo

class Redirect(Resource):
    def __init__(self, url):
        self.url = url
        Resource.__init__(self)

    def render_GET(self, request):
        return redirectTo(self.url, request)
