""" cortex.services.web.resource
"""
import re
import types
import inspect
import simplejson

from goulash import Namespace
from jinja2.loaders import TemplateNotFound
from twisted.web.resource import Resource

from cortex.core import api
from cortex.core.hds import HDS
from cortex.core.agent import Agent
from cortex.services.api import API
from cortex.core.ground import Memory
from cortex.services import Service
from cortex.agents.proc import Process
from cortex.core.universe import Universe
from cortex.mixins.autonomy import Autonomy
from cortex.core.util import report, pedigree
from cortex.services.postoffice import PostOffice
from cortex.services.web.template import template
from .util import get_source, alligator2paren

ATOMS = ( list, tuple,  float, int, basestring )

post_processors = type('sdasdasd',(object,),
                       dict(reverse_console = staticmethod(report.console.html)))

class EFrame(Resource):
    def render_GET(self, request):
        chan = request.args['chan'][0]
        url = 'http://{0}:{1}/alerts?{2}'.format(self.universe.host,
                                               self.ehub.port,chan)
        ctx = dict(eframe_url=url,)
        t = template('eframe')
        return str(t.render(**ctx))

class ObjectResource(Resource):
    isLeaf = True

    def __init__(self, obj):
        self._obj = obj

    @property
    def is_atom(self): return isinstance(self.target, ATOMS)

    @property
    def is_complex(self): return not self.is_atom

    def _from_req(self, name):
        return self.request.args[name][0]

    @property
    def template(self):
        """ """
        ctx = {}
        target = self.target

        if 'force_template' in self.request.args:
            T = self._from_req('force_template')
            T = 'objects/'+T
            T = template(T)
        else:
            try:
                file_name = inspect.getfile(target)
            except TypeError:
                try:
                    file_name = self.target.__module__
                except AttributeError:
                    file_name = '(unknown)'

            tname = type(target).__name__.lower()
            try:
                T = template('objects/' + tname)
            except TemplateNotFound:
                report('greedy failed', tname)
                tname = None
                T = None

            ctx.update(file_name=file_name,
                       source=get_source(target))

            if T is not None:
                report("greedy found T", tname)

            elif self.is_atom:
                T = template('objects/primitive')


            elif target == Universe:
                T = template('objects/universe')
                ctx.update(procs=Universe.procs + [Universe.pid],
                           threads=Universe.threads,
                           )
            elif isinstance(target, Agent):
                T = template('objects/agent')
                _pedigree = [ [x[0], x[1].__name__] \
                              for x in pedigree(target).items() \
                              if x[1] is not None ]
                ctx.update(parent=alligator2paren(target.parent),
                           pedigree=_pedigree,
                           subscriptions=getattr(getattr(target,'Meta',None),
                                                 'subscriptions',[]),
                           autonomy=Namespace(target).intersection(Namespace(Autonomy)))
                if isinstance(target, Process):
                    T = template('objects/agent_process')

                if isinstance(target, Service):
                    T = template('objects/services/service')
                    children = target.agents if hasattr(target, 'agents') else []
                    ctx.update(children=children)

                if isinstance(target, API):
                    T = template('objects/services/api')
                    ctx.update(api_methods=api.publish())

                if isinstance(target, PostOffice):
                    T = template('objects/services/postoffice')

            elif isinstance(target, Memory):
                # keep this one after postoffice
                T = template('objects/memory')

            elif isinstance(target, HDS):
                T = template('objects/HDS')
            elif isinstance(target,
                            types.MethodType):
                T = template('objects/method')
            else:
                T = template('objects/abstract')
        return T, ctx

    def breadcrumbs(self,request):
        """ """
        out = filter(None, request.path.split('/'))
        z = []
        for x in out:
            upto = out.index(x)+1
            tmp  = [x, out[:upto]]
            z.append(tmp)
        result = ['<a href={0}> {1} </a>'.format(
            '/' + '/'.join(x[1]),x[0]) for x in z]
        if len(result) > 6: result = result[-6:]
        return result

    def _dispatcher(self, request):
        for k in request.args:
            func_name = '_dispatch_' + k
            if hasattr(self, func_name ):
                return getattr(self,func_name)

    def _dispatch_call(self, request):
        name = request.args['call'][0]
        return alligator2paren(getattr(self.target, name)())

    def _dispatch_getattr(self, request):
        name = request.args['getattr'][0]
        return alligator2paren(getattr(self.target, name, 'N/A'))

    def render_pedigree_json(self, obj_path):
        obj_path.remove('inheritance.json')
        self.target = self.resolve_object(obj_path)
        self.request.setHeader("content-type", "text/json")
        edges = []
        def classtree(cls):
            for supercls in cls.__bases__:
                if supercls==object: continue
                edges.append(dict(source=supercls.__name__,
                                  target=cls.__name__,
                                  type='notset'))
                classtree(supercls)
        classtree(self.target.__class__)
        return simplejson.dumps(edges)

    def render_GET(self, request):
        """ """
        self.request = request
        obj_path = filter(None, self.request.postpath)

        if 'inheritance.json' in obj_path:
            return self.render_pedigree_json(obj_path)

        self.target = self.resolve_object(obj_path)
        dispatch_to = self._dispatcher(request)
        if dispatch_to is not None:
            return dispatch_to(request)
        breadcrumbs = self.breadcrumbs(request)
        ctx = dict(obj=self.target, path=request.postpath,
                   breadcrumbs=breadcrumbs,
                   request=request,)

        if self.is_complex:
            ns = Namespace(self.target, dictionaries=False)
            try:
                ns_locals = ns.methods.locals
            except:
                ns_locals = ['error_retrieving_local_methods']

            ctx.update(all_namespace=ns.keys(),
                       ns_methods=ns.methods.nonprivate,
                       ns_locals=ns_locals,
                       ns_private=ns.private,
                       ns_data=ns.data,
                       )
        ctx.update(base_url=request.path, obj_name=self.obj_name)
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
                #if isinstance(target, (list,tuple)): index = int(index)
                if hasattr(target, '__getitem__'):
                    try: index = int(index)
                    except ValueError: pass
                target   = target[index]
            elif component.endswith('()'):
                func   = component[:-2]
                target = getattr(target,func)()
            else:
                target = getattr(target, component)
        if 'postprocess' in self.request.args:
            func = getattr(post_processors, self._from_req('postprocess'))
            target = func(target)
        return target

    @property
    def obj_name(self):
        obj_name = getattr(self.target, '__name__', str(self.target))
        obj_name = alligator2paren(obj_name)
        obj_name = obj_name.replace('object at','@')
        return obj_name
ObjResource = ObjectResource
