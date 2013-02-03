""" cai1.py

    This is the Cortex-as-Interpreter-Demo, version 1.
    Only run this file with the cortex interpretter.

    ABOUT
    ----------------------------------------------------------------------------
    All versions of the Cortex-As-Interpreter-Demo are equivalent, and in fact
    are equivalent to the Simple-Demo
    Each version shows various ways of architecting the solution.


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

# uncomment the next line to see more noise from the whole system
#import cortex; cortex.VERBOSE = True

# set up enough services to support this demo and allow user to inspect it
__instructions__ = [ ["load_service", "web"],
                     ["load_service", "terminal"],
                     ["load_service", "postoffice"] ]

# create a simple Agent template with no concurrency.  agent's of this
# type will generate a random signal of values in [0,1].  we will defer
# the decision of how to actually run this agent, and just say that here
# is something that happens repeatedly when it runs.
@ Agent.from_function
def SigGen(self):
    self.value = random.random()

# create a different kind of agent template.  this agent will run be
# registered last so it will bootstrap last, and here we'll only need
# one instance of the final product.
@ Agent.from_function
def OnReady(universe):
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
    long_url = multiplot.wrapped_url + '&Title=AgentDemo'
    _, short_url = web.make_redirect('demo', long_url)
    open_demo = lambda *args: (universe|'web').open_page_in_browser(short_url)
    (universe|'terminal').contribute_to_api(open_demo=open_demo)
    report('to open a the url for the demo type: ", open_demo"')

# a list of unique agent-iteration intervals.
# we'll end up creating one agent for each speed.
AGENT_ITERATION_SPEEDS = [.1, .2, .3,]

# create a special list (__agents__).
#  __universe__.agents.manage() will be called
# for every item in this list.
__agents__ = []
for speed in AGENT_ITERATION_SPEEDS:
    # create a new type of Agent, binding both
    # the template and a specific flavor of autonomy.
    # the iteration speed will affect the specifics
    # of the autonomy.
    __agents__.append(
        Agent.using(template=SigGen,
                    flavor=ReactorRecursion,
                    extras={'period':speed,
                            'name':'Agent'+str(speed)}))
__agents__ += [OnReady]

# everything is ready.  since this demo is run directly with the 'cortex'
# commandline, there's no need to hit the button and start the universe..
# it's implied that the universe will play() after this file is done
# executing.
