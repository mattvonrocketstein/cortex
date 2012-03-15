""" cortex.services.web.resource
"""
import types
import inspect

from twisted.web.resource import Resource
from cortex.util.namespaces import NSPart
from cortex.services.web.template import template
from cortex.core.agent import Agent

class Root(Resource):
    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

class ObjectResource(Resource):
    isLeaf = True

    def __init__(self, obj):
        self._obj = obj

    @property
    def is_atom(self):
        return isinstance(self.target, ( int, str ))

    @property
    def is_complex(self):
        return not self.is_atom

    @property
    def template(self):
        if isinstance(self.target, Agent):
            return template('objects/agent'),{}
        elif isinstance(self.target, types.MethodType):
            return template('objects/method'),dict(source=inspect.getsource(self.target))
        elif self.is_atom:
            return template('objects/primitive'),{}
        else:
            return template('objects/abstract'),{}

    def render_GET(self, request):
        """ """
        obj_path = filter(None, request.postpath)
        self.target = self._obj
        while obj_path: self.target = getattr(self.target, obj_path.pop(0))
        ctx = dict(obj=self.target, path=request.postpath, request=request,)
        if self.is_complex:
            ns = NSPart(self.target)
            ctx.update(all_namespace=sorted(ns.namespace.keys()),
                       methods=sorted(ns.methods.keys()),
                       private=sorted(ns.private.keys()))
        obj_name = getattr(self.target, '__name__', str(self.target))
        obj_name = obj_name.replace('<','(').replace('>',')')
        ctx.update(obj_name=obj_name)
        t,extra_ctx=self.template
        ctx.update(**extra_ctx)
        return str(t.render(**ctx))
ObjResource=ObjectResource
