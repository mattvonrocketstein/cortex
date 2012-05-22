""" cortex.core.service
"""

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

    def _boot_order_constraint(self, s1, boot_order1, s2, boot_order2):
        """ returns True iff if s1, s2 satisfy the
                constraint when they have boot-order

                   s1 := boot_order1,
                   s2 := boot_order2
        """

        # all boot orders should be unique.
        if boot_order1==boot_order2:
            return False

        # figure out which service is first
        first, second = (s1, s2) if (boot_order1 < boot_order2) else (s2, s1)

        # ensure the second isn't in the first's
        #  table of dependancies
        if second in self.table[first]: return False
        else:                           return True

    def build_constraint_table(self):
        """ TODO: allow multiple boot-first constraints?
        """
        from collections import defaultdict
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


    def resolve_boot_order(self, **kargs):
        """ TODO: try a different underlying CSP algorithm? it looks like
                  with some (inconsistent) initial conditions, and using
                  min-conflicts this can run for a num_steps:=very_large_number
                  before *proving* the system is inconsistent and giving up?

            NOTE: kargs will be passed on to the CSP-solving-algorithm that is chosen.
        """

        # Build table of start._boot_first constraints
        self.build_constraint_table()

        names = [x[0] for x in self._pending]

        # neighbors: every service participates in the
        # constraints of the other selfs except itself
        neighbors = dict([ [service, [service2 for service2 in names if \
                                      service2!=service]] for service in names ])

        # vars: variables to solve over
        vars = [ name for name in names ]

        # domains: every service could potentially be booted in any order
        domains = dict([ [service, range(len(names))] for service in names])

        # the totality of the problem.  nothing to do with this now, but here it is.
        csp_definition = dict( vars = vars, domains = domains, neighbors = neighbors,
                               constraint = self._boot_order_constraint )

        # compute solution
        csp_problem    = csp.CSP(vars, domains, neighbors, self._boot_order_constraint)
        #csp_algorithm  = csp.min_conflicts #backtracking_search #AC3 #
        csp_algorithm  = csp.backtracking_search #AC3 #
        answer         = csp_algorithm(csp_problem, **kargs)
        nassigns       = csp_problem.nassigns

        # clean up the answer: it will be a dictionary of {service_name:boot_order},
        #  but boot_order's may be duplicated, and it may not be in order.
        answer = answer.items()
        answer.sort(lambda x,y: cmp(x[1], y[1]))
        return [ x[0] for x in answer ]


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

class FecundService(Service, AgentManager):
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
        child_classes = self.__class__.Meta.children
        for kls in child_classes:
            name = kls.__name__
            kargs = dict(kls=kls, kls_kargs=ctx, name=name)
            self.manage(**kargs)
        self.load()
        Service.start(self)
