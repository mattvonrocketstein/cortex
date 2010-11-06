""" cortex.core.universe
"""
import os
import inspect
import simplejson
from tempfile import NamedTemporaryFile

#from twisted.internet import gtk2reactor
#gtk2reactor.install()
from twisted.internet import reactor

from cortex.util import Memoize
from cortex.core.reloading import AutoReloader
from cortex.core.util import report, console
from cortex.core.atoms import AutonomyMixin, PerspectiveMixin
from cortex.core.atoms import PersistenceMixin
from cortex.core.services import ServiceManager,Service

def getAnswer(Q, yesAction=None, noAction=None, dispatcher=None):
    """ getAnswer: ask a "yes or no" question, dispatch to an action
        (possibly the empty-action) based on user-response on stdin

          Some Shortcuts w/ Questions:
             <Q> will be given a question mark if it doesn't have one,
             <Q> capitalization will be formulated as if a book title
    """
    ans = "JUNK_DATA"
    if not Q.endswith('?'): Q += '?'
    question = Q.title()
    question+=' [y/n] > '
    while ans not in 'ynYN':
        ans = raw_input(question)
    if ans.lower()=='y':   ans = True;  result = yesAction and yesAction()
    elif ans.lower()=='n': ans = False; result = noAction and noAction()
    return ans,result


class __Universe__(AutoReloader, AutonomyMixin, PerspectiveMixin,
                   PersistenceMixin):
    """
        NOTE: this should effectively be a singleton
    """
    testing = 131231111115
    node_list = []
    _services = []

    """
    class shell:
         a dumb abstraction for a shell rooted at <path>
        def __init__(self, path):
            self.path = path

        def __call__(self, line, quiet=False):
            """ """
            os.system('cd "'+path+'"; '+line)
    """
    reactor = reactor
    def tmpfile(self):
        """ return a new temporary file """
        tmpdir = os.path.join(self.instance_dir, 'tmp')
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        f = NamedTemporaryFile(delete=False,dir=tmpdir)
        return f

    def leave(self, other=None):
        """ other begs universe for permission to leave """
        #self.nodes.remove()
        def detect_other():
            pass
        if other==None:
            other = detect_other()
        pass

    def read_nodeconf(self):
        """ iterator that returns decoded json entries from self.nodeconf_file
        """
        assert hasattr(self, 'nodeconf_file') and self.nodeconf_file, 'Universe.nodeconf_file tests false or is not set.'
        #report("Universe.nodeconf: decoding")
        x = open(self.nodeconf_file).readlines()
        x = [z.strip() for z in x]
        nodes = []
        for line in x:
            if not line:
                continue
            #report('got line', line)
            try:
                nodedef = simplejson.loads(line)
            except:
                report("error decoding..", line)
            else:
                #report('encoded..', nodedef)
                nodes.append(nodedef)
        return nodes

    @property
    def Nodes(self):
        """ nodes: static definition """
        return self.read_nodeconf()

    @property
    def threads(self):
        import threading
        return threading.enumerate()

    @property
    def nodes(self):
        """ nodes: dynamic definition """
        return self.node_list

    def stop(self):
        for service in self.services:
            try: service.stop()
            except Exception,e:
                print 'exc',e
                #IP.quitting=True
        self.started = False
        for thr in self.threads:
            thr._Thread__stop()
        self.reactor.stop()
    def play(self):
        """
            Post:
                self.node_list = [ <list of active nodes> ]
        """
        report("Universe.play!")
        self.started = True
        # Starts all nodes registered via the nodeconf
        if hasattr(self, 'nodeconf_file') and self.nodeconf_file:
            for node in self.read_nodeconf():
                name, kargs = node
                kargs.update( {'name':name,'universe':self} )
                node = self.launch_instance(**kargs)
                self.node_list.append(node)

        # Start special services provided by the universe
        for service in self.Services:
            report('launching service',service)
            self.loadService(service)


        #report('running reactor')
        # Main loop
        reactor.run()
    def loadService(self,service):
        """ """
        if isinstance(service, str):
            if "." in service:
                raise Exception,'will not interpret dotpath yet'
            else:
                import inspect
                ns={}
                exec('from cortex.core.services import '+service+' as mod',ns)
                mod = ns['mod']
                for name in dir(mod):
                    val = getattr(mod,name)
                    if inspect.isclass(val):
                        if not val==Service and issubclass(val, Service):
                            #launch_service = lambda: val(universe=self).play
                            print 'discovered service in ', mod.__name__,'@',mod.__file__
                            ret = val(universe=self).play()
                            self._services.append(ret)
                            return ret
                            #getAnswer('launch service@'+str([name, val]),
                            #          yesAction=val(universe=self).play)
        else:
            ret = service(universe=self).play()
            self._services.append(ret)
            return ret

    @property
    @Memoize
    def services(self):
        """ services: dynamic definition

            this represents services that have already been
            successfully started.
        """
        return ServiceManager(self._services)

    @property
    def Services(self):
        """ services: static definition

            computes services from defaults,
             command line arguments, and
              node definition files.
        """
        #[self.stdoutbeacon_service, self.filercvr]
        from cortex.core.services.terminal import Terminal
        from cortex.core.services.beacon import Beacon
        from cortex.core.services._linda import Linda
        _Services = [Linda, Terminal]
        # _Services.append(Beacon)
        return _Services

    def django_service(self):
        """  Start special services provided by the universe """
        import django.core.handlers.wsgi
        application = django.core.handlers.wsgi.WSGIHandler()

    def launch_instance(self, **kargs):
        from cortex.core.node import Node
        report(**kargs)
        node = Node(**kargs)
        report(node)
        console.draw_line()
        node.play()
        return node

Universe = __Universe__()
