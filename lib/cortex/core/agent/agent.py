""" cortex.core.agent
"""

import os
import time

from pep362 import Signature

from cortex.core.util import report
from cortex.core.metaclasses import META1
from cortex.core.common import AgentError
from cortex.core.data import NOOP, LOOPBACK_HOST, GENERIC_LOCALHOST
from cortex.mixins import AutonomyMixin, PerspectiveMixin
from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from channel import is_declared_callback,unpack, declare_callback
from cortex.core.data import DEFAULT_HOST
from cortex.mixins import MobileCodeMixin
from cortex.mixins import FaultTolerant
from cortex.core.manager import Manager

class Agent(MobileCodeMixin, AutonomyMixin, PerspectiveMixin, FaultTolerant):
    """
        CONVENTION: __init__ always passes unconsumed kargs to _post_init()

        TODO: move SelfHostingTupleBus and FOL-KB into agents-proper
        TODO: Make mixin classes work with __add__

    """
    __metaclass__ = META1 # a metaclass that tracks all the subclasses for this class
    _post_init    = NOOP
    name          = 'default-name'

    @classmethod
    def using(self, template=None, flavor=None):
        target=Agent
        if template:
            target = target.template_from(template)
        if flavor:
            target=target.use_concurrency_scheme(flavor)
        return target

    @classmethod
    def use_concurrency_scheme(kls, other):
        """ uses the concurrency scheme ``other``
            mutate this agent-subclass in place to prefer Autonomy
            methods described in the autonomy subclass ``other``
        """
        return type('asdasdasd', tuple([other]) + kls.__bases__, {})


    @classmethod
    def template_from(this_kls, cls_template):
        """ return a new class that has all the behaviour specified in ``cls_template``
            as well as at least the minimum requirements of being an abstract Agent.

            ``cls_template`` is a dictionary-like item that has named behaviours
        """
        return type('outer(inner)'.format(outer=this_kls.__name__,
                                          inner=cls_template.__name__),
                    (this_kls,cls_template),
                    {})


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

    def __init__(self, host=None, universe=None, name=None, **kargs):
        """
            TODO: "host" is bad.  use a better address formalism instead.
        """
        self.universe = universe
        self.host     = host or DEFAULT_HOST
        self.name     = name
        cbs = [ getattr(self,x) for x in dir(self) if is_declared_callback(getattr(self,x)) ]
        for cb in cbs:
            cb.bootstrap(self)
        self._post_init(**kargs)

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

    # def play(self): inherited from Autonomy

Node    = Agent         # Alias
