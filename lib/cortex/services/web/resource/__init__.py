""" cortex.services.web.resource
"""
import re
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

from cortex.core.universe import Universe
from cortex.services.web.resource.root import Root

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


def get_source(obj):
    if obj==type:
        return 'Could not retrieve source.'
    try:
        return inspect.getsource(obj)
    except:
        return get_source(obj.__class__)


def classtree(cls, indent=0, out='', base_url='', pfx=[]):
    cname = cls.__name__
    if cname=='object': return ''
    link = '<a class="adepth_{0}" href="{1}">{2}</a>'
    link = link.format(indent, '/'.join(map(str, pfx)), cname)
    out += ('<br/>' if indent else '') + '.'*indent + ' ' + link
    for supercls in cls.__bases__:
        rellink  = base_url + ('/__class__/' if not indent else '')
        rellink += '__bases__[{0}]'.format(cls.__bases__.index(supercls))
        out += classtree(supercls, indent+1, pfx=pfx + [rellink])
    return out

class ObjectResource(Resource):
    isLeaf = True

    def __init__(self, obj):
        self._obj = obj

    @property
    def is_atom(self):
        return isinstance(self.target, ( tuple, int, str ))

    @property
    def is_complex(self):
        return not self.is_atom

    @property
    def template(self):
        """ """
        ctx = {}
        if self.is_atom:
            T = template('objects/primitive')
        else:
            ctx.update(source=get_source(self.target))
<<<<<<< Updated upstream
            if isinstance(self.target, Agent):
                T = template('objects/agent')
            elif self.target == Universe:
                T = template('objects/universe')
            elif isinstance(self.target, types.MethodType):
=======
            from cortex.services.web import Service
            target=self.target
            if False:
                pass
            elif target == Universe:
                T = template('objects/universe')
            elif isinstance(target, Agent):
                from cortex.mixins.autonomy import Autonomy
                T = template('objects/agent')
                ctx.update(parent=str(target.parent).replace('<','(').replace('>',')'),
                           autonomy=NSPart(target).intersection(NSPart(Autonomy)))
                if isinstance(target, Service):
                    T = template('objects/service',)
                    ctx.update(children=target.agents if hasattr(target, 'agents') else [],)
                    #ctx.update()
            elif isinstance(target, HDS):
                T = template('objects/HDS')
            elif isinstance(target, types.MethodType):
>>>>>>> Stashed changes
                T = template('objects/method')
            else: T = template('objects/abstract')
        return T, ctx

    def breadcrumbs(self,request):
        out = filter(None,request.path.split('/'))
        z = []
        for x in out:
            z.append([x,out[:out.index(x)+1]])
        result = ['<a href={0}> {1} </a>'.format('/' + '/'.join(x[1]),x[0]) for x in z]
        if len(result) > 6: result = result[-6:]
        return result


    def render_GET(self, request):
        """ """
        obj_path = filter(None, request.postpath)
        self.target = self.resolve_object(obj_path)
        breadcrumbs = self.breadcrumbs(request)
        ctx = dict(obj=self.target, path=request.postpath,
                   breadcrumbs=breadcrumbs,
                   ancestry=classtree(getattr(self.target,'__class__',object),
                                      base_url=request.path),
                   request=request,)
        def rsorted(a,b):
            try: x = getattr(a,b).keys()
            except:
                return ['error in rsorted']
            x = reversed(sorted(x))
            return x

        if self.is_complex:
            ns = NSPart(self.target)
            ctx.update(all_namespace=rsorted(ns,'namespace'),
                       methods=rsorted(ns,'methods'),
                       private=rsorted(ns,'private')
                       )
        obj_name = getattr(self.target, '__name__', str(self.target))
        obj_name = obj_name.replace('<','(').replace('>',')')
        obj_name = obj_name.replace('object at','@')
        ctx.update(obj_name=obj_name)
        t,extra_ctx=self.template
        ctx.update(**extra_ctx)
        return str(t.render(**ctx))

    def resolve_object(self, obj_path, target=None):
        target   = target or self._obj
        while obj_path:
            component = obj_path.pop(0)
            if '[' in component:
                x = '\[.*\]'
                m = re.search(x, component)
                if not m: raise RuntimeError,"bad url?"
                span     = m.span()
                index    = component.__getslice__(*span)[1 : -1]
                jst_name = component[:span[0]]
                target   = getattr(target, jst_name)
                if isinstance(target,(list,tuple)): index = int(index)
                target   = target[index]
            else:
                target = getattr(target, component)
        return target

    def obj_name(self, target):
        obj_name = getattr(target, '__name__', str(target))
        obj_name = obj_name.replace('<','(').replace('>',')')
        return obj_name

    """ def render_GET(self, request):

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
        return str(_template.render(**ctx))"""
ObjResource = ObjectResource
