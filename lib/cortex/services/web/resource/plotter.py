""" cortex.services.web.resource.plotter
"""

from .cortex_base import CBR
from .data_source import DataSource

from cortex.services.web.template import template

class Plotter(CBR):
    """ """
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

class Multiplotter(Plotter):
    """ naked multiplotter: no wrapper"""
    def __init__(self,wrapped=False):
        self.wrapped=wrapped
        Plotter.__init__(self)

    def getChild(self, name, request):
        from cortex.services.web.util import Multiplot
        from cortex.services.web.resource.redirect import Redirect
        if name in Multiplot.registry:
            mplot = Multiplot.registry[name]
            return Redirect(mplot.url)
        return Plotter.getChild(self,name,request)

    def get_template_ctx(self, request):
        multiplot_title = request.args.get('Title',['Title'])
        endpoints = request.args.get('endpoint', [])
        titles   = request.args.get('title', [])
        data = dict(zip(titles, endpoints))
        ctx  = dict(multiplot_title=multiplot_title[0], data=data)
        template = ('wrapped_multiplotter' if self.wrapped else 'multiplotter')
        return template, ctx
