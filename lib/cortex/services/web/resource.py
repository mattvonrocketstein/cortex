""" cortex.services.web.resource
"""

import time
import types
import inspect

from twisted.web.resource import Resource
from cortex.util.namespaces import NSPart
from cortex.services.web.template import template
from cortex.core.agent import Agent

from twisted.internet import reactor, task
from twisted.web.server import Site
from twisted.web import server
from twisted.web.resource import Resource

from twisted.internet.task import deferLater
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor

class ClockPage(Resource):
    def _delayedRender(self, request):
        request.write("<html><body>")#Sorry to keep you waiting.</body></html>")
        request.write("Sorry")

        time.sleep(1)
        request.write("to keep")

        time.sleep(1)
        request.write("you ")

        time.sleep(1)
        request.write("waiting.</body></html>")
        request.finish()

    def render_GET(self, request):
        d = deferLater(reactor, 1, lambda: request)
        d.addCallback(self._delayedRender)
        return NOT_DONE_YET

class ClockPage2(Resource):
    isLeaf = True
    def __init__(self):
        self.presence = []
        loopingCall = task.LoopingCall(self.__print_time)
        loopingCall.start(1, False)
        Resource.__init__(self)

    def render_GET(self, request):
        request.write('&lt;b&gt;%s&lt;/b&gt;' % (time.ctime(),))
        self.presence.append(request)
        server.NOT_DONE_YET
        yield str('testing')

    def __print_time(self):
        for p in self.presence:
            p.write('&lt;b&gt;%s&lt;/b&gt;' % (time.ctime(),))


class Root(Resource):
    def getChild(self, name, request):
        if name == '': return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        """ """
        children = self.children.copy()
        children.pop('static','')
        children.pop('favicon.ico','')
        ctx = dict(children=children,
                   contents=dir(self))
        return str(template('root').render(**ctx))

class ObjectResource(Resource):
    isLeaf = True

    def __init__(self, obj):
        self._obj = obj

<<<<<<< HEAD
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
=======
    def resolve_object(self, obj_path, target=None):
        target   = target or self._obj
        while obj_path:
            target = getattr(target, obj_path.pop(0))
        return target

    def obj_name(self, target):
        obj_name = getattr(target, '__name__', str(target))
        obj_name = obj_name.replace('<','(').replace('>',')')
        return obj_name

    def is_atom(self, target):
        return isinstance(target, (int,str))

    def render_GET(self, request):
        """ """
        obj_path  = filter(None, request.postpath)
        target    = self.resolve_object(obj_path)
        ctx       = dict(path=request.postpath, request=request)
        _atom     = self.is_atom(target)
        _complex  = not _atom
        _template = template('objects/primitive') if _atom \
                   else self.template
        if _complex:
            ns = NSPart(target)
            ctx.update(all_namespace=ns.namespace.keys(),
                       methods=ns.methods.keys(),
                       private=ns.private.keys())
        ctx.update(obj_name=self.obj_name(target))
        return str(_template.render(**ctx))
ObjResource = ObjectResource
