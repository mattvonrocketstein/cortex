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

    class docFactory:
        @staticmethod
        def load(ctx=None, preprocessors=()):
            return "EventHub, rootpage"

    def child_alerts ( self, ctx ):
        return AlertPage(self.eventHandler)

    def child_event ( self, ctx ):
        return CreateEventPage(self.eventHandler)
