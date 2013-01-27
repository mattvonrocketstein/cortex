"""
"""
import random
import webbrowser

import cortex
from cortex.core.agent import Agent
from cortex.core.universe import Universe
from cortex.mixins.flavors import ReactorRecursion

universe = Universe
cortex.VERBOSE = True

# set up enough services to support this demo and allow user to inspect it
universe.set_nodes([ ["load_service", "web"],
                     ["load_service", "terminal"],
                     ["load_service", "postoffice"], ])

# create a simple Agent template with no concurrency.  agent's of this
# type will generate a random signal of values in [0,1].  we will defer
# the decision of how to actually run this agent, and just say that here
# is something that happens repeatedly when it runs.
@ Agent.from_function
def SigGen(self):
    self.value = random.random()

@ Agent.from_function
def OnReady(universe):
    """ """
    # ask the universe to give us a handle for the web service
    web = (universe|'web')

    # create a multiplot instance
    multiplot = web.new_multiplot()

    # this factory takes in an agent-name and return a function
    # which can be polled to return the current signal-value
    datagen_factory = lambda name: lambda: (universe**name).value

    # isolate only the signal-generator agents and iterate over them.
    # for each one we make the multiplot aware of names (which will be
    # translated to url-endpoints) and a method for converting that name
    # to a function which can return measurements on the corresponding
    # signal.
    signal_generators = universe.agents.filter_by_type(SigGen)
    for signal_generating_agent in signal_generators:
        name = signal_generating_agent.name
        multiplot.install_subplot(name, datagen_factory(name))

    # everything has been registered with the multiplot, so now connect
    # the endpoints.  all url endpoints will be connected to the generators
    multiplot.install_streams()

    # the multiplot url is safe to access now that the instance is
    # totally configured, but that url is complex with a disgusting
    # large querystring.  for convenience, the next line makes a redirect
    # from '/demo', and opens a webbrowser there.
    _, short_url = web.make_redirect('demo', multiplot.url)
    webbrowser.open_new_tab(short_url)

# a list of unique agent-iteration intervals.
# we'll end up creating one agent for each speed.
AGENT_ITERATION_SPEEDS = [.1, 1, 3]

for speed in AGENT_ITERATION_SPEEDS:
    # create a unique name for each unique speed
    agent_name = 'Agent' + str(speed)
    # create a new type of Agent, binding both
    # the template and a specific flavor of autonomy.
    # the iteration speed will affect the specifics
    # of the autonomy.
    AgentKlass = Agent.using(template=SigGen,
                             flavor=ReactorRecursion)

    AgentKlass.period = speed

    #
    universe.agents.manage(agent_name, kls=AgentKlass)





# Order matters here
universe.agents.manage('OnReady', kls=OnReady)

universe.play()
