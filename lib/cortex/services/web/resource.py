"""
"""
from twisted.web.resource import Resource

from cortex.util.namespaces import NSPart
from cortex.services.web.template import template

class Root(Resource):
    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

class ObjectResource(Resource):
    isLeaf = True

    @property
    def template(self):
        return template('objects/abstract')

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
        _template = template('objects/primitive') if _atom \
                   else self.template
        if _complex:
            ns = NSPart(target)
            ctx.update(all_namespace=ns.namespace.keys(),
                       methods=ns.methods.keys(),
                       private=ns.private.keys())
        obj_name = getattr(target, '__name__', str(target))
        obj_name = obj_name.replace('<','(').replace('>',')')
        ctx.update(obj_name=obj_name)

        return str(_template.render(**ctx))
ObjResource=ObjectResource
