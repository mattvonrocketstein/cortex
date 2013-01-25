""" cortex.services.web.resource.conf_resource

    dumb resource to display the current configuration file
"""


from twisted.web.resource import Resource

from cortex.services.web.template import template

class ConfResource(Resource):
    """ dumb resource to display the configuration file """

    def __init__(self, universe):
        self.universe = universe

    def current_contents(self):
        return open(self.universe.nodeconf_file).read()

    def render_GET(self, request):
        ctx = dict(filename=self.universe.nodeconf_file,
                   text=self.current_contents())
        return str(template('nodeconf').render(**ctx))
