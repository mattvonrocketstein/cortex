""" cortex.core.universe.reactor
"""

from twisted.internet import reactor

from cortex.core.util import report
from multiprocessing import Process

class ReactorAspect(object):
    reactor       = reactor
    callLater     = reactor.callLater
    listenTCP     = reactor.listenTCP
    getThreadPool = reactor.getThreadPool

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
