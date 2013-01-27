""" simpledemo2.py

    This is the Simple-Demo, version 2.  Run this file with python directly.

    ABOUT
    ----------------------------------------------------------------------------
    All versions of the Simple Demo are equivalent, but show various ways of
    architecting the solution.

    Every Simple-Demo shows how to create simple agents that generate and store
    random numbers at different speeds.  After creating and starting all
    the agents, a new browser tab will be opened that shows a dynamic graph
    that represents the internal state of those agents.

    THIS VERSION
    ----------------------------------------------------------------------------
    This version of the demo creates agents using a mix of python-style
    inheritance and cortex-style class-generation.

"""
import random
import webbrowser

from cortex.core.agent import Agent
from cortex.core.universe import Universe
from cortex.mixins.flavors import ReactorRecursion

# uncomment the next line to see more noise from the whole system
#import cortex; cortex.VERBOSE = True

# set up enough services to support this demo and allow user to inspect it
Universe.set_instructions([ ["load_service", "web"],
                            ["load_service", "terminal"],
                            ["load_service", "postoffice"], ])

# create a simple Agent template with no concurrency.  agent's of this
# type will generate a random signal of values in [0,1].  we will defer
# the decision of how to actually run this agent, and just say that here
# is something that happens repeatedly when it runs.
class SigGen(Agent):

    def iterate(self):
        self.value = random.random()

    def install_plot(self, multiplot):
        multiplot.install_subplot(self.name, lambda: self.value)

# create a different kind of agent template.  this agent will run be
# registered last so it will bootstrap last, and here we'll only need
# one instance of the final product.
class OnReady(Agent):

    def build_multiplot(self):
        # ask the universe to give us a handle for the web service;
        # create a multiplot instance
        web = (self.universe|'web')
        multiplot = web.new_multiplot()

        # isolate only the signal-generator agents and iterate over them.
        # for each one we make the multiplot aware of names (which will be
        # translated to url-endpoints) and a method for converting that name
        # to a function which can return measurements on the corresponding
        # signal.
        signal_generators = self.universe.agents.filter_by_type(SigGen)
        for siggen_agent in signal_generators:
            siggen_agent.install_plot(multiplot)

        # everything has been registered with the multiplot, so now connect
        # the endpoints.  all url endpoints will be connected to the generators
        multiplot.install_streams()
        return multiplot

    def iterate(self):
        # configure the multiplot instance
        multiplot = self.build_multiplot()

        # get a handle for the web service and install a redirect.
        #
        # the multiplot url is safe to access now that the instance is
        # totally configured, but that url is complex with a disgusting
        # large querystring.  for convenience, the next line makes a redirect
        # from '/demo', and opens a webbrowser there.
        web = (self.universe|'web')
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
                             flavor=ReactorRecursion,
                             extras=dict(period=speed))
    # this is essentially a deferred instantiation of the
    # agent.  (we can't instantiate it because that's the
    # job of the universe once it's bootstrapped).  we
    # register the agent type with a universe, and give the
    # name the instance will use.
    Universe.agents.manage(agent_name, kls=AgentKlass)

# another request for registration/delayed instantiation.
# as mentioned above it's definiton, the OnReady agent will
# bootstrap our setup after the universe itself is finished
# boostrapping.
Universe.agents.manage('OnReady', kls=OnReady)

# everything is ready.  hit the button and start the universe
Universe.play()
