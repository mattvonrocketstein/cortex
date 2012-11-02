""" cortex.core.universe.reactor
"""

from multiprocessing import Process

from twisted.internet import reactor

from cortex.core.util import getcaller
from cortex.core.util import report


class ReactorAspect(object):
    reactor       = reactor
    callLater     = reactor.callLater
    listenTCP     = reactor.listenTCP
    getThreadPool = reactor.getThreadPool

    def listenTCP(self, port, factory, backlog=50, interface=''):
        """ 1) find out which agent wants to use this port,
            2) log it in self.ports
            3) chain to the real listenTCP
        """
        caller = getcaller()
        # try getting the instance,
        # failing that use the class
        owner = caller.get('self', None)
        if owner is None:
            owner = caller.get('kls', 'unknown')
        self.ports[port] += [owner]
        return reactor.listenTCP(port, factory, backlog=backlog, interface=interface)

    def callInProcess(self, target, args=tuple(),
                      name='DefaultProcessName', delay=1, **kargs):
        """ """
        p = Process(target=target, args=args, name=name, **kargs)
        def start():
            self.procs.append(p)
            report('starting process "{0}" ({1} total)'.format(p.name, len(self.procs)))
            p.start()
        def finish():
            p.join()
            self.procs.remove(p)
            report('finished with process "{0}" ({1} left)'.format(p.name,len(self.procs)))

        def go():
            start()
            finish()
        self.callLater(delay, go)
