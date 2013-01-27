"""
graphing options:

  d3:
    http://bost.ocks.org/mike/path/

  cubism: ?

  float:
    http://people.iola.dk/olau/flot/examples/realtime.html
    http://people.iola.dk/olau/flot/examples/

"""
import urllib
import random
import webbrowser
from optparse import OptionParser
from urllib import urlencode as urlenc

import cortex
from cortex.core.util import report
from cortex.core.agent import Agent
from cortex.core.universe import Universe
from cortex.mixins.flavors import ReactorRecursion

universe = Universe
cortex.VERBOSE = True

@ Agent.from_function
def SigGen(self):
    self.value = random.random()

@ Agent.from_function
def OnReady(universe):
    """
        install a redirect:
          "/demo" -> <multiplotterUrl>
        install data-streams:
          from each agent to /x and /y
        compute the absolute url and open it in a webbrowser
  """
    web = (universe|'web')
    root = web.children()[0]
    x_axis_args = urlenc(dict(endpoint='/x', title='X_axis'))
    y_axis_args = urlenc(dict(endpoint='/y', title='Y_axis'))
    full_url = 'multiplot?' + '&'.join([x_axis_args,y_axis_args])
    demo_url = 'demo'
    web.make_redirect(demo_url, full_url)
    get_x = lambda: (universe**'Axis1').value
    get_y = lambda: (universe**'Axis2').value
    web.make_data_stream('x', get_x)
    web.make_data_stream('y', get_y)
    demo_url = 'http://{0}:{1}/{2}'.\
               format(universe.host,
                      universe.port_for(root),
                      demo_url)
    webbrowser.open_new_tab(demo_url)

X_axis = Agent.using(template=SigGen, flavor=ReactorRecursion)
Y_axis = Agent.using(template=SigGen, flavor=ReactorRecursion)
X_axis.period = 2

# Order matters here
universe.agents.manage('Axis1',   kls=X_axis,  kls_kargs={})
universe.agents.manage('Axis2',   kls=Y_axis,  kls_kargs={})
universe.agents.manage('OnReady', kls=OnReady, kls_kargs={})

default_nodes = [ ["load_service", "web"],
                  ["load_service", "api"],
                  ["load_service", "terminal"],
                  ["load_service", "postoffice"],
                  ["load_service", "network_mapper"], ]
universe.set_nodes(default_nodes)
universe.play()
