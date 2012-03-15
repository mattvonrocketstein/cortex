"""
"""
from nevow import loaders, tags as T, inevow, rend

class EventHandler():
    def __init__(self):
        self.subscriberList = []

    def addSubscriber(self, subscriber):
        self.subscriberList.append(subscriber)

    def fireEvent(self, eventID):
        for subscriber in self.subscriberList:
            subscriber.fireEvent(eventID)

class EventCreator(rend.Page):
    def __init__(self,eventHandler):
        self.eventHandler = eventHandler

    def render_body ( self, ctx, data ):
        request = inevow.IRequest ( ctx )
        f = request.fields
        eventID = json.dumps(['/'.join(filter(None, request.path.split('/'))[1:]),
                              dict([[x, f[x].value] for x in f])])
        self.eventHandler.fireEvent(eventID)
        return "Event Created with ID: %s" % (eventID,)

    docFactory = loaders.stan (
        T.html [ T.head [T.title["Event Created"]],
                 T.body [ render_body ]
        ])

class CreateEventPage(rend.Page):
    def __init__(self, eventHandler):
        self.eventHandler = eventHandler

    docFactory = loaders.stan(T.html[
        T.head(title = "Create an Event"),
        T.body[ "Create an Event by visiting /event/<ID of event to be created>"]
        ])

    def locateChild ( self, ctx, segments ):
        return ( EventCreator(self.eventHandler), () )
import json
