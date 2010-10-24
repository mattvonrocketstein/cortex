""" go.py: Second-phase init
"""

import os
from cortex import core
from cortex.core.universe import Universe
# You need to override this for your project,
#   or define a project file.
NODE_CONF = None

#os.environ['DJANGO_SETTINGS_MODULE'] = ''
#from twisted.internet import reactor
#from twisted.internet import stdio
#from twisted.internet.protocol import Factory
#from cortex.core.rcvr import RCVR
#universe = core.universe

def go_django():
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

def main():
    """
    """
    instance_dir = os.path.split(__file__)[0]
    #NODE_CONF = NODE_CONF or os.path.join(__file__,'.nodeconf')
    #assert os.path.exists(NODE_CONF), "You need to define a NODE_CONF@"+NODE_CONF
    Universe.launch_instance(host="127.0.0.1",
                             resource_description={},
                             instance=instance_dir)
    #Universe.load_nodeconf(project_dir)
    #universe['terminal'] = core.Terminal()
    #stdio.StandardIO(universe['terminal'])

    #pf = Factory()
    #pf.clients = []
    #pf.protocol = core.RCVR
    #reactor.listenTCP(1234, pf)

    #from cortex.core.rcvr import FileIOFactory
    #fileio = FileIOFactory({})
    #reactor.listenTCP(1234, fileio)
    #reactor.run()

if __name__ == '__main__':
    main()
