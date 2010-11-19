""" cortex.core.service
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.util import report, console
from cortex.core.ground import HierarchicalWrapper, HierarchicalData


def resolve_boot_order(universe,**kargs):
    """ """
    services = universe.services
    from cortex.contrib.aima.csp import CSP, min_conflicts

    def service_constraint(s1, boot_order1, s2, boot_order2):
        """ returns True iff if services s1, s2 satisfy the
            constraint when they have boot-order

               s1 := boot_order1,
               s2 := boot_order2
        """

        if boot_order1 <= boot_order2:
            first, second = s1, s2
        else:
            first, second = s2, s1

        if second in (universe|first)._boot_first:
            return False
        else:
            return True

    # vars: variables to solve over,
    # domains: every service could potentially be booted in any order
    # neighbors: every service participates in the constraints of the other services except itself
    # service_constraint(A,a,B,b) := True when A=a;B=b is legal
    csp_definition = dict( vars       = [service for service in services],
                           domains     = dict([ [service, range(len(services))] for service in services]),
                           neighbors   = dict([ [service, [service2 for service2 in services if \
                                                                service2!=service]] for service in services]),
                           constraint = service_constraint)
    csp_problem    = CSP(csp_definition['vars'],
                         csp_definition['domains'],
                         csp_definition['neighbors'],
                         csp_definition['constraint'])
    csp_algorithm  = min_conflicts
    ans            = csp_algorithm(csp_problem, **kargs)
    for (var, val) in ans.items():
        print '\t',var,val
    return csp_problem.nassigns, ans


class ServiceManager(Manager):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """
    asset_class = HierarchicalData
    def __init__(self, *args, **kargs):
        """ """
        self.registry      = {}
        self.generic_store = HierarchicalWrapper('server_obj') #generic storage for the actual manager itself.

    def stop_all(self):
        """ """
        [ s.stop() for s in self ]


class Service(Node):
    """
    """

    def __init__(self, *args, **kargs):
        """ """

        # a list of items that have to be play()'ed before this service
        self._boot_first = []

        if 'name' in kargs:
            raise Exception,'services specify their own names'
        else:
            kargs.update( { 'name' : self.__class__.__name__ } )

        super(Service,self).__init__(*args, **kargs)

    @property
    def status(self):
        """ placeholder """
        return self.is_stopped,self.started

    def __repr__(self):
        """ """
        return '<{name}-Service {_id}>'.format(_id=str(id(self)),
                                               name=self.__class__.__name__)

    def _post_init(self, **kargs):
        """ """
        self.is_stopped = False

    def stop(self):
        """ """
        report("service::stopping")
        self.is_stopped = True
        self.started    = False
        super(Service,self).stop()

    def play(self):
        """
            Convention: services *must* define start() and stop(), therefore
                        the functionality of <play> is implied.
        """
        self.universe.reactor.callLater(1, self.start)
        return self
SERVICES = ServiceManager()
