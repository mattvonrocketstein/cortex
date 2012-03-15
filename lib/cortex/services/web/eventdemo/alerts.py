from nevow import athena,loaders, tags as T, inevow, rend
from twisted.python import filepath,util
from events import EventHandler

class AlertElement(athena.LiveElement):
    jsClass = u'Alerts.AlertWidget'
    _tpl = filepath.FilePath(__file__).parent().child('templates').child('alerts_table.html')
    docFactory = loaders.xmlfile(_tpl.path)

    def __init__(self, eventHandler, *a, **kw):
        super(AlertElement, self).__init__(*a, **kw)
        eventHandler.addSubscriber(self)

    def fireEvent(self, eventID):
        self.callRemote('addRow', unicode(eventID))

class AlertPage(athena.LivePage):
    def __init__(self, eventHandler, *a, **kw):
        super(AlertPage, self).__init__(*a,**kw)
        self.eventHandler = eventHandler
        modulePath = filepath.FilePath(__file__).parent().child('js').child('alerts.js')
        self.jsModules.mapping.update({
            'Alerts': modulePath.path})

    docFactory = loaders.stan(T.html[
        T.head(render=T.directive('liveglue')),
        T.body(render=T.directive('alertElement'))])

    def render_alertElement(self, ctx, data):
        f = AlertElement(self.eventHandler)
        f.setFragmentParent(self)
        return ctx.tag[f]
