""" cortex.services.web

      a template service. does nothing, but useful to copy
"""
import os

from twisted.web import static, server

import cortex
from cortex.core.util import report
from cortex.services import Service
from cortex.util.decorators import constraint
from cortex.util.namespaces import NSPart

from twisted.web.resource import Resource
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('cortex.services.web', 'templates'))


class Root(Resource):
    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

class MyResource(Resource):
    isLeaf = True

    @property
    def template(self):
        return env.get_template('abstract_object.html')

    def __init__(self, obj):
        self._obj = obj

    def render_GET(self, request):
        """ """
        obj_path = filter(None,request.postpath)
        target   = self._obj

        while obj_path:
            target = getattr(target,obj_path.pop(0))
        ctx = dict(path=request.postpath,
                   request=request,

                   )
        _atom    = isinstance(target,(int,str))
        _complex = not _atom
        template = env.get_template('primitive_object.html') if _atom \
                   else self.template
        if _complex:
            template = self.template
            ns = NSPart(target)
            ctx.update(all_namespace=ns.namespace.keys(),
                       methods=ns.methods.keys(),
                       private=ns.private.keys())
        obj_name = getattr(target, '__name__', str(target))
        obj_name = obj_name.replace('<','(').replace('>',')')
        ctx.update(obj_name=obj_name)

        return str(template.render(**ctx))


class Web(Service):
    """ Stub Service:
        start: brief description of service start-up here
        stop:  brief description service shutdown here
    """
    def print_error(self, *errors):
        """ """
        for x in errors:
            pass # choose any errors to ignore and remove them
        report('error_handler for generic service', str(errors) )

    def stop(self):
        """ """
        Service.stop(self)
        report('Custom stop for', self)

    # toggle the decorator below to register constraints,
    # e.g. which named services this service will depend on
    #@constraint(boot_first='postoffice')
    def start(self):
        """ <start> is an operation, called once (and typically by <play>), which may or
            may not return and so may be blocking or non-blocking.

            most blocking services will either a) need to be wrapped to made non-blocking,
            or, b) they may responsibly manage their own mainloop using some combination
            of this function and iterate()
        """
        d = os.path.dirname(__file__)
        code_dir = os.path.dirname(cortex.__file__)
        static_dir = os.path.join(d,'static')
        favicon = os.path.join(static_dir,'favicon.ico')

        root = Root()
        root.putChild('static',      static.File(static_dir))
        root.putChild('favicon.ico', static.File(favicon))
        root.putChild('web',         MyResource(self))
        root.putChild("_code",       static.File(code_dir))
        self.universe.reactor.listenTCP(1338, server.Site(root))
        Service.start(self)
        report('Finished bootstrapping', self)

    def iterate(self):
        """ a placeholder for some "probably-atomic-action".
            this name is used by convention ie if <start> invokes
            it repeatedly as in from a while-loop or "reactor-recursion"
            with reactor.callLater
        """
        pass

    def play(self):
        """ <play> is stubbed out although services should usually
            override <start> instead.
        """
        return Service.play(self)
