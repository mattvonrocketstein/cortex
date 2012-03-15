from nevow import athena,loaders, tags as T, inevow, rend
from events import EventHandler, CreateEventPage
from alerts import AlertPage

class RootPage(rend.Page):
    pass

class RootPage2(rend.Page):
    isLeaf=True

    def __init__ ( self, *args, **kwargs ):
        rend.Page.__init__ ( self, *args, **kwargs )
        self.eventHandler = EventHandler()

    addSlash = True
    def render(self, *args, **kargs):
        print args,kargs
        out = self.docFactory.load()
        return ''.join(out)

    class docFactory:
        @staticmethod
        def load(ctx=None, preprocessors=()):
            print ctx
            return loaders.stan(T.html[
                T.head[T.title["Root Page"]],
                T.body[ T.h1["Index"],
                        T.h2 [T.a ( href = 'alerts' ) [ "Alerts Page" ]],
                        T.h2 [T.a ( href = 'event' ) [ "Generate an event"]]
                        ]]).load(ctx, preprocessors)

    def child_alerts ( self, ctx ):
        return AlertPage(self.eventHandler)

    def child_event ( self, ctx ):
        return CreateEventPage(self.eventHandler)
