""" go.py: second phase init
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = ''

from twisted.internet import reactor
from twisted.internet import stdio
from twisted.internet.protocol import Factory

from cortex.core.rcvr import RCVR

from cortex import core
universe = core.universe

def go_django():
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

def main():
    universe['terminal'] = core.Terminal()
    stdio.StandardIO(universe['terminal'])

    #pf = Factory()
    #pf.clients = []
    #pf.protocol = core.RCVR
    #reactor.listenTCP(1234, pf)

    from cortex.core.rcvr import FileIOFactory
    fileio = FileIOFactory({})
    reactor.listenTCP(1234, fileio)

    reactor.run()

if __name__ == '__main__':
    main()
