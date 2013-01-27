"""
"""
import random
import webbrowser

import cortex
from cortex.core.agent import Agent
from cortex.core.universe import Universe
from cortex.mixins.flavors import ReactorRecursion
from cortex.services.web.util import Multiplot

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
    multiplot = Multiplot(web)
    datagen = lambda name: lambda: (universe**name).value
    for signal_generating_agent in universe.agents.values():
        name = signal_generating_agent.name
        if name.lower().startswith('onready'): continue
        multiplot.install_subplot(name, datagen(name))
    multiplot.install_streams()
    _, short_url = web.make_redirect('demo', multiplot.url)#full_url)
    webbrowser.open_new_tab(short_url)

for agent_num in '123':
    AgentN = Agent.using(template=SigGen, flavor=ReactorRecursion)
    universe.agents.manage('Agent'+agent_num,  kls=AgentN,  kls_kargs={})
    AgentN.period = int(agent_num)

# Order matters here
universe.agents.manage('OnReady', kls=OnReady, kls_kargs={})

default_nodes = [ ["load_service", "web"],
                  ["load_service", "api"],
                  ["load_service", "terminal"],
                  ["load_service", "postoffice"], ]

universe.set_nodes(default_nodes)
universe.play()
