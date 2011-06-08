"""
"""

import inspect
import types
from cortex.core.agent import Agent

from cortex.core.util import report

def namespace(obj):
    return dict([ [ name, getattr(obj,name)] for name in dir(obj) if not name.startswith('_')])

class agentifier(object):
    """ a naive thing that turns other kinds of things into agents """
    @property
    def universe(self):
        from cortex.core.api import universe
        return universe

    def ClassType(self,obj):
        from threading import Thread
        if issubclass(kls, Thread):
            from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        else:
            raise Exception,"dont know how to translate that classobj yet"

    def FunctionType(self, func):
        print self.universe
        out = Agent.subclass(iterate=func)
        return out(universe=self.universe)

    def InstanceType(self, obj):
        if isinstance(obj, obj): pass
        raise Exception,"Don't know how to agentize {o}".format(o=other)

    def __call__(self, other):
        global types
        for name,t in namespace(types).items():
         if isinstance(other,t):
             handler=getattr(self, name, None)
             report("Using handler {h} on {o}".format(h=handler,o=other))
             if handler:
                 return handler(other)
        raise Exception,"Unknown type(other)"
    """
        if inspect.isclass(other):
            return self.from_class(other)
        elif isinstance(other,FunctionType):
            return self.from_function(other)
        else:
            return self.from_object(other)
    """
agentifier=agentifier()
