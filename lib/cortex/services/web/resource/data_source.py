""" cortex.services.web.resource.data_source
"""

from .json import JSONResource

class DataSource(JSONResource):

    def __init__(self, method):
        self.method = method
        JSONResource.__init__(self)

    def render_JSON(self, request):
        result = self.method()
        assert isinstance(result, (float, int))
        return result
