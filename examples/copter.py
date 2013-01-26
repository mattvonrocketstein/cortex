"""
graphing options:

  d3:
    http://bost.ocks.org/mike/path/

  cubism: ?

  float:
    http://people.iola.dk/olau/flot/examples/realtime.html
    http://people.iola.dk/olau/flot/examples/

"""
import random
from optparse import OptionParser

import cortex
from cortex.core.universe import Universe
from cortex.core.agent import Agent
from cortex.core.util import report
from cortex.mixins.flavors import ReactorRecursion
from cortex.mixins import Mixin
from channel.exceptions import ChannelExists
universe = Universe
cortex.VERBOSE = True
COLLECTOR = 'collector'

class SigGen(Mixin):
    """ generate a stream of random numbers and shout them out """

    period = 1

    def get_value(self):
        return self.value

    def iterate(self):
        self.value = random.random()

@ Agent.from_function
def OnReady(universe):
    web = (universe|'web')
    x = universe.agents['Axis1'].obj
    y = universe.agents['Axis2'].obj
    web.make_data_stream('x', x.get_value)
    web.make_data_stream('y', y.get_value)

AXIS_1 = Agent.using(template=SigGen, flavor=ReactorRecursion)
AXIS_2 = Agent.using(template=SigGen, flavor=ReactorRecursion)

# Order matters here
universe.agents.manage('Axis1', kls=AXIS_1, kls_kargs={})
universe.agents.manage('Axis2', kls=AXIS_2, kls_kargs={})
universe.agents.manage('OnReady', kls=OnReady, kls_kargs={})

universe.set_nodes([["load_service", "postoffice"],
                    ["load_service", "network_mapper"],
                    ["load_service", "web"],
                    ["load_service", "api"],
                    ["load_service", "terminal"], ])
universe.play()
#
