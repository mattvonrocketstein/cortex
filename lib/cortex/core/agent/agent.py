""" cortex.core.agent
"""
import time

from pep362 import Signature

from goulash.metaclasses import META1
from cortex.core.common import AgentError
from cortex.core.data import NOOP, DEFAULT_HOST
from cortex.mixins.topology import TopologyMixin
from cortex.core.agent.comms_mixin import CommsMixin
from cortex.core.util import report, report_if_verbose
from cortex.mixins import (Mixin, AutonomyMixin, FaultTolerant, MobileCodeMixin)

from spock import Doctrine

class AgentLite(TopologyMixin, MobileCodeMixin,
                AutonomyMixin, FaultTolerant):
    """
    """
    @classmethod
    def using(self, template=None, flavor=None, extras={}):
        """
           usage:
              Agent.using(template=SomeMixin,flavor=SomeAutonomyFlavor)
        """
        target = Agent
        if isinstance(template, dict):
            template.update(extras)
            template = type('DynamicMixin',(Mixin,), template)
        elif extras:
            template = type('DynamicMixin', (template,), extras)
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
    def from_function(kls, fxn, flavor=None):
        """ heuristic for building agents from functions """
        sig = Signature(fxn)
        sig_args = set(sig._parameters.keys())
        if set(['universe'])==sig_args:
            def iterate(himself):
                return fxn(himself.universe)
        elif set(['self']) == sig_args:
            iterate = fxn
        else:
            err = 'Not sure how to build iterate method for args: '
            raise RuntimeError(err+str(sig_args))
        dct = dict(iterate=iterate)
        kls_name = fxn.__name__
        bases=(kls,)
        return type(kls_name, bases, dct)

class LogicMixin(object):

    @property
    def beliefs(self):
        """ """
        if not hasattr(self,'_beliefs'):
            self._beliefs = Doctrine()
        return self._beliefs

class Agent(LogicMixin, CommsMixin, AgentLite):
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
    def parent(self):
        """ Warning this might not be an agent! """
        if len(self.parents):
            if len(self.parents)<2: return self.parents[0]
            else: self.fault('ambiguous topology')
        else:
            return None

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
