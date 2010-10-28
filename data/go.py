""" go.py: Second-phase init

    Scratchpad:


#os.environ['DJANGO_SETTINGS_MODULE'] = ''
#from twisted.internet import reactor
#from twisted.internet import stdio
#from twisted.internet.protocol import Factory
#from cortex.core.rcvr import RCVR
#universe = core.universe


    #from cortex.core.rcvr import FileIOFactory
    #fileio = FileIOFactory({})
    #reactor.listenTCP(1234, fileio)
    #reactor.run()

"""

import os
from cortex import core
from cortex.core.universe import Universe
from cortex.core.util import report

NODE_CONF = None #'node.conf'

def main():
    """ """
    # Set node configuration file in universe
    instance_dir = os.path.split(__file__)[0]
    nodeconf_file = NODE_CONF or os.path.join(instance_dir, 'node.conf')
    if not os.path.exists(nodeconf_file):
        report("Expected node.conf @ "+nodeconf_file+', None found.')
        Universe.nodeconf_file = None
    else:
        Universe.nodeconf_file = nodeconf_file

if __name__ == '__main__':
    main()
    Universe.play() # Invoke the Universe

if __name__ == '__main__':
    main()
