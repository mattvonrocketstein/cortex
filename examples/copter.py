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

name_to_plot_args = lambda name: \
            urlenc(dict(endpoint='/'+(universe**name).name,
                        title=(universe**name).name))
def make_data_stream(web, name):
    web.make_data_stream((universe**name).name,
                         lambda: (universe**name).value)
class Multiplot(object):
    def __init__(self):
        self.subplots = {}
        self.endpoint_root = '/'
        self.multiplot_url = 'multiplot'

    def install_subplot(self, name, data_generator):
        self.subplots[name] = data_generator

    @property
    def url(self):
        full_url = self.multiplot_url + '?'
        for name in self.subplots:
            full_url += '&' + \
                        urlenc(dict(endpoint=self.endpoint_root + name,
                                    title=name))
        return full_url

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
    names = 'X_axis','Y_axis'
    multiplot = Multiplot()
    #full_url = 'multiplot?'
    for name in names:
        #full_url += '&' + name_to_plot_args(name)
        multiplot.install_subplot(name, lambda: (universe**name).value)
        make_data_stream(web, name)
    _, short_url = web.make_redirect('demo', multiplot.url)#full_url)
    webbrowser.open_new_tab(short_url)

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
