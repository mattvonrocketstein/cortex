""" cortex.services.web.resource.json
"""
import demjson

from twisted.web.resource import Resource

class JSONResource(Resource):
   def render_GET(self, request):
       request.setHeader("content-type", "text/json")
       return str(demjson.encode(self.render_JSON(request)))
