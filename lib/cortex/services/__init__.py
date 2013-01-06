""" cortex.core.service
"""
from collections import defaultdict

from cortex.core.util import report, console
from cortex.core.data import NOOP
from cortex.contrib.aima import csp
from cortex.core.agent import Agent, AgentManager
from cortex.core.manager import Manager


class ServiceManager(AgentManager):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """

    # TODO: might need an abstractagentmanager..
    pre_load_obj      = Manager.pre_load_obj

    def pre_manage(self, name=None, kls=None, **kls_kargs):
        """ undo agentmanager's hook for pre_manager.. """
        return name, kls, kls_kargs

    def build_constraint_table(self):
        self.table = defaultdict(lambda:[])
        for item in self._pending:
            name, kls, kargs = item
            tmp = getattr(kls.start, '_constraint_boot_first', [])
            if not isinstance(tmp,(list,tuple)): tmp = [tmp]
            self.table[name] += tmp
        for item in self.table:
            self.table[item] = filter(None, self.table[item])
        self.table = dict(self.table)
        return self.table


    def resolve_boot_order(self):
        # Build table of start._boot_first constraints
        from spock import BootOrderProblem
        self.build_constraint_table()
        return BootOrderProblem(self.table)()


class Service(Agent):
    """ Abstractions representing a cortex service
    """
    class ServiceError(Exception):
        """ Move along, nothing to see here """

    def _raise_error(self, msg):
        """ helper for informative exceptions """
        formatting = dict(msg=msg, service_name=self.__class__.__name__)
        msg = 'Problem with Service@"{service_name}": {msg}'.format(**formatting)
        raise Service.ServiceError(msg)

    def __init__(self, *args, **kargs):
        """ """
        # a list of items that have to be play()'ed before this service
        self._boot_first = []

        if 'name' in kargs:
            self._raise_error('Services specify their own names!')
        else:
            kargs.update( { 'name' : self.__class__.__name__ } )

        super(Service,self).__init__(*args, **kargs)

    @property
    def status(self):
        """ placeholder """
        return self.is_stopped, self.started

    def __repr__(self):
        """ """
        formatting = dict(_id  = str(id(self)),
                          name = self.__class__.__name__)
        return '<{name}-Service {_id}>'.format(**formatting)

    def stop(self):
        """ Convention:
              <stop> for services differs from your typical
              agent because ?
        """
        super(Service, self).stop()
        if isinstance(self, AgentManager):
            self.stop_all()

    def play(self):
        """
            Convention:
              services *must* define <start> and <stop>,
              therefore the functionality of <play> is implied;
              you should not need to override this method.

        """
        self.universe.reactor.callWhenRunning(self.start)
        return self

# A cheap singleton
SERVICES = ServiceManager()
from cortex.mixins.topology import TopologyMixin as _TopologyMixin
class TopologyMixin(_TopologyMixin):
    def children(self):
        children_names = [ name for name in self ]
        children = [self[name].obj for name in children_names]
        return super(TopologyMixin, self).children() + children

class FecundService(TopologyMixin, Service, AgentManager):
    """ FecundService describes a service with children.

        You get mostly the semantics you'd expect.  When the
        parent is start()'ed, the children start, and similarly
        for stop().

        To use, subclassers should define a Meta like this:


           class Meta:
               children = [ChildClass-1, ChildClass-2, .. ]
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kargs):
        Service.__init__(self, **kargs)
        AgentManager.__init__(self, **kargs)

    def start(self):
        """ """
        ctx = dict(universe=self.universe)
        child_classes = self._opts.children
        for kls in child_classes:
            name = kls.__name__
            kargs = dict(kls=kls, kls_kargs=ctx, name=name)
            self.manage(**kargs)
        self.load()
        Service.start(self)
