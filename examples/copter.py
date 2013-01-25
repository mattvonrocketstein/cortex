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
        postoffice = (self.universe|'postoffice')
        postoffice.publish(COLLECTOR, self.name,
                           self.value)

class Collector(Agent):
    """ 1) creates channel in postoffice.. this is awkward
        2) collect the numbers that are shouted for all axis
    """
    class Meta: subscriptions = {COLLECTOR : 'collector'}
    def collector(self, name, i, **kargs):
        pass #print name, '::', i , kargs

    def setup(self):
        try:
            (self.universe|'postoffice').add_channel(COLLECTOR)
        except ChannelExists: pass

@Agent.from_function
def OnReady(universe):
    web = (universe|'web')
    x = universe.agents['Axis1'].obj
    y = universe.agents['Axis2'].obj
    z = universe.agents['Axis3'].obj
    web.make_data_stream('x', x.get_value)
    web.make_data_stream('y', y.get_value)
    web.make_data_stream('z', z.get_value)

AXIS_1 = Agent.using(template=SigGen, flavor=ReactorRecursion)
AXIS_2 = Agent.using(template=SigGen, flavor=ReactorRecursion)
AXIS_3 = Agent.using(template=SigGen, flavor=ReactorRecursion)

universe.agents.manage('Collector', kls=Collector, kls_kargs={})
universe.agents.manage('Axis1', kls=AXIS_1, kls_kargs={})
universe.agents.manage('Axis2', kls=AXIS_2, kls_kargs={})
universe.agents.manage('Axis3', kls=AXIS_3, kls_kargs={})
universe.agents.manage('OnReady', kls=OnReady, kls_kargs={})

universe.set_nodes([["load_service", "postoffice"],
                    ["load_service", "network_mapper"],
                    ["load_service", "web"],
                    ["load_service", "api"],
                    ["load_service", "terminal"], ])
universe.play()
#
