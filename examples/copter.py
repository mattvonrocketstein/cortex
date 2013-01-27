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
    name2args = lambda name: \
                urlenc(dict(endpoint='/'+(universe**name).name,
                            title=(universe**name).name))
    full_url = 'multiplot?' + '&'.join([name2args('X_axis'),
                                        name2args('Y_axis')])
    demo_url = 'demo'
    web.make_redirect(demo_url, full_url)
    get_x = lambda: (universe**'X_axis').value
    get_y = lambda: (universe**'Y_axis').value
    web.make_data_stream((universe**'X_axis').name, get_x)
    web.make_data_stream((universe**'Y_axis').name, get_y)
    demo_url = 'http://{0}:{1}/{2}'.\
               format(universe.host,
                      universe.port_for(root),
                      demo_url)
    webbrowser.open_new_tab(demo_url)

X_axis = Agent.using(template=SigGen, flavor=ReactorRecursion)
Y_axis = Agent.using(template=SigGen, flavor=ReactorRecursion)
X_axis.period = 2

# Order matters here
universe.agents.manage('X_axis',  kls=X_axis,  kls_kargs={})
universe.agents.manage('Y_axis',  kls=Y_axis,  kls_kargs={})
universe.agents.manage('OnReady', kls=OnReady, kls_kargs={})

default_nodes = [ ["load_service", "web"],
                  ["load_service", "api"],
                  ["load_service", "terminal"],
                  ["load_service", "postoffice"],
                  ["load_service", "network_mapper"], ]
universe.set_nodes(default_nodes)
universe.play()
