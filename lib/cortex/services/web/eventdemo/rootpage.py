from cortex.services.web.template import template
from nevow import athena,loaders, tags as T, inevow, rend
from events import EventHandler, CreateEventPage
from alerts import AlertPage

class RootPage(rend.Page):
    pass

class RootPage2(rend.Page):
    isLeaf = True
    addSlash = True

    def __init__ ( self, *args, **kwargs ):
        rend.Page.__init__ ( self, *args, **kwargs )
        self.eventHandler = EventHandler()

    #def getChild(self, name, request):
    #    print '*'*80,name,request
    #    return None

    #def render(self, request, *args, **kargs):
    #    path = filter(None,request.path.split('/'))[1:]
    #    print path, args, kargs
    #    name = path.pop(0)
    #    method = getattr(self,'child_'+name,None)
    #    if method is not None:
    #        return str(method(request).load(ctx))
    #    out = self.docFactory.load()
    #    return ''.join(out)

    class docFactory:
        @staticmethod
        def load(ctx=None, preprocessors=()):
            return template('edemo_base').render()
            print ctx
            result = loaders.stan(T.html[
                T.head[T.title["Root Page"]],
                T.body[ T.h1["Index"],
                    T.h2 [T.a ( href = 'alerts' ) [ "Alerts Page" ]],
                    T.h2 [T.a ( href = 'event' ) [ "Generate an event"]]
                        ]]).load(None, preprocessors={})
            print result
            return result

    def child_alerts ( self, ctx ):
        return AlertPage(self.eventHandler)

    def child_event ( self, ctx ):
        return CreateEventPage(self.eventHandler)
