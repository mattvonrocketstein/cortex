""" cortex.services.web.resource.plotter
"""

from .cortex_base import CBR
from .data_source import DataSource

from cortex.services.web.template import template

class Plotter(CBR):

    def __init__(self):
        CBR.__init__(self)
        import random;
        ds = DataSource(lambda:random.random())
        self.putChild('data_stream', ds)

    def get_template_ctx(self, request):
        endpoint = request.args.get('endpoint', None)
        ctx = dict(title=request.args.get('title', ['default title'])[0],)
        if endpoint:
            ctx.update(endpoint=endpoint[0])
        return 'plotter',ctx
