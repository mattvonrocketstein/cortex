""" cortex.core.agent
"""
import time

from pep362 import Signature

from cortex.core.metaclasses import META1
from cortex.core.common import AgentError
from cortex.core.data import NOOP, DEFAULT_HOST
from cortex.mixins.topology import TopologyMixin
from cortex.core.agent.comms_mixin import CommsMixin
from cortex.core.util import report, report_if_verbose
from cortex.mixins import (AutonomyMixin, FaultTolerant, MobileCodeMixin)

from spock import Doctrine

class AgentLite(TopologyMixin, MobileCodeMixin,
                AutonomyMixin, FaultTolerant):
    """
    """
    pass

class Agent(CommsMixin, AgentLite):
    """
        CONVENTION: __init__ always passes unconsumed kargs to _post_init()

        TODO: move SelfHostingTupleBus and FOL-KB into agents-proper
        TODO: Make mixin classes work with __add__

    """
    __metaclass__ = META1 # a metaclass that tracks all the subclasses for this class
    _post_init    = NOOP
    _instances    = []
    name          = 'default-name'

    @property
    def _opts(self):
        return getattr(self.__class__,'Meta', None)

    def __init__(self, host=None, universe=None, name=None, **kargs):
        """
            TODO: "host" is bad.  use a better address formalism instead.
        """
        self.universe = universe
        self.host     = host or DEFAULT_HOST
        self.name     = name
        self.parents  = []
        self._handle_embedded_callbacks()
        Agent._instances.append(self)
        self._post_init(**kargs)

    @property
    def beliefs(self):
        """ """
        if not hasattr(self,'_beliefs'):
            self._beliefs = Doctrine()
        return self._beliefs

    @property
    def parent(self):
        """ Warning this might not be an agent! """
        if len(self.parents):
            if len(self.parents)<2: return self.parents[0]
            else: self.fault('ambiguous topology')
        else:
            return None

    @classmethod
    def using(self, template=None, flavor=None):
        """
           usage:
              Agent.using(template=SomeMixin,flavor=SomeAutonomyFlavor)
        """
        target = Agent
        if flavor:
            target = target.use_concurrency_scheme(flavor)
        if template:
            target = target.template_from(template)
        return target

    @classmethod
    def use_concurrency_scheme(kls, other):
        """ uses the concurrency scheme ``other``
            mutate this agent-subclass in place to prefer Autonomy
            methods described in the autonomy subclass ``other``
        """
        kls_name = '{0}+{1}'.format(other.__class__.__name__,
                                    kls.__name__)
        return type(kls_name, tuple([other, kls ]) , {})


    @classmethod
    def template_from(this_kls, cls_template):
        """ return a new class that has all the behaviour specified in ``cls_template``
            as well as at least the minimum requirements of being an abstract Agent.

            ``cls_template`` is a dictionary-like item that has named behaviours
        """
        kls_name = '{outer}({inner})'.format(outer=this_kls.__name__,
                                             inner=cls_template.__name__)
        bases = (cls_template, this_kls)
        dct = {}
        return type(kls_name, bases, dct)

    def __repr__(self):
        return "<{name}>".format(name=self.name)

    def wait(self, arg=1): time.sleep(arg)

    @classmethod
    def _subclass_hooks(kls, name=None, iterate=None, **dct):
        """ the following two should be equivalent,
            because in the first case "self" is implied:

              >>> A = Agent.subclass(iterate=lambda:dostuff(1,2,3) )
              >>> A = Agent.subclass(iterate=lambda self:dostuff(1,2,3) )

           both of these are equivalent to:
              >>> class A(Agent):
              >>>     def iterate(self):
              >>>         dostufff(1,2,3)
        """
        if iterate is not None:
            sig = Signature(iterate)
            new_iterate = iterate
            if not sig._parameters:
                new_iterate = lambda self: iterate()
            dct['iterate'] = new_iterate
        return name,dct

    def start(self):
        """ """
        super(Agent, self).start()
        self._handle_Meta_subscriptions()

    def stop(self):
        """ autonomy override:
            by convention, usage of <stop> shows that this agents
            is stopping himself.  (if other agents are able to stop
            this agent, it is more appropriate to use <halt> or
            <shutdown> instead.)
        """
        super(Agent, self).stop()

    def iterate(self):
        """ Convention:
              <iterate> is typically called by <play>, but
              whereas <play> is (under normal circumstances)
              only called once, <iterate> may be called several
              times.
        """

    @property
    def siblings(self):
        out = [ x for x in self.parent.children() if x!=self ]
        out = dict([ [x.name, x] for x in out ])
        return out

    # play(self):: inherited from Autonomy

Node    = Agent         # Alias
