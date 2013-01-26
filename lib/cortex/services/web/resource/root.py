""" cortex.services.web.resource.root
"""

from twisted.web.resource import Resource
from twisted.web import static as _static

from .cortex_base import CBR

class Root(CBR):
    def __init__(self, favicon=None, static=None):
        Resource.__init__(self)
        self.putChild('static',      _static.File(static))
        self.putChild('favicon.ico', _static.File(favicon))
        self.putChild('main_nav',    NavResource())
        self.redirect_map = {}

    def render_GET(self, request):
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
#if request.path in self.redirect_map:
        return CBR.render_GET(self, request)

    def get_template_ctx(self, request):
        """ """
        children = self.children.copy()
        universe = self.parent.universe
        clo = universe.command_line_options._getLeaves()
        return ('root',
                dict(boot_order=universe.services._boot_order,
                     command_line_options = clo,
                     children=children,
                     contents=dir(self)))

class NavResource(CBR):
    """ TODO: generate this automatically """
    isLeaf = True
    @property
    def _children(self):
        return 'universe web conf _code '.split()
    def get_template_ctx(self, request):
        return ('nav', dict(children=self._children,))
