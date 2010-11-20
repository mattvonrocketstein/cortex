""" cortex.core.service
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.util import report, console
from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from cortex.contrib.aima.csp import CSP, min_conflicts
from cortex.core.data import NOOP
class ServiceManager(Manager):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """
    asset_class = HierarchicalData

    def items(self):
        """ dictionary compatability """
        return [[var, val.service_obj] for var,val in Manager.items(self)]

    def __init__(self, *args, **kargs):
        """ """
        self.registry      = {}

        # TODO: when in doubt, autoproxy to..
        self.generic_store = HierarchicalWrapper('server_obj')

    def stop_all(self):
        """ stop all services this manager knows about """
        [ s.stop() for s in self ]
    post_registration = NOOP
    #@finished_successfully_event('new_manager__{name}'.format(name=name))
    def register(self, name, **service_metadata):
        """ """
        Manager.register(self, name, **service_metadata)
        #print '*'*99, getattr(service_metadata['service_obj'].start,'summary_annotations',lambda: 'empty')()
        #self[name].constraints = {'boot_before': service_metadata['service_obj']._boot_first}

    def _boot_order_constraint(self, s1, boot_order1, s2, boot_order2):
            """ returns True iff if self s1, s2 satisfy the
                constraint when they have boot-order

                   s1 := boot_order1,
                   s2 := boot_order2
            """
            if boot_order1 <= boot_order2:
                first, second = s1, s2
            else:
                first, second = s2, s1

            if second in self[first].service_obj._boot_first:
                return False
            else: return True

    def resolve_boot_order(self, **kargs):
        """ TODO: try a different underlying CSP algorithm? it looks like
                  with some (inconsistent) initial conditions, and using
                  min-conflicts this can run for a num_steps:=very_large_number
                  before *proving* the system is inconsistent and giving up?

            NOTE: kargs will be passed on to the CSP-solving-algorithm that is chosen.
        """

        # neighbors: every service participates in the constraints of the other self except itself
        neighbors = dict([ [service, [service2 for service2 in self if \
                                      service2!=service]] for service in self])

        # vars: variables to solve over
        vars       = [service for service in self],

        # domains: every service could potentially be booted in any order
        domains     = dict([ [service, range(len(self))] for service in self])

        # the totality of the problem.  nothing to do with this now, but here it is.
        csp_definition = dict( vars = vars, domains = domains, neighbors = neighbors,
                               constraint = self._boot_order_constraint )
        # compute solution
        csp_problem    = CSP(vars, domains, neighbors, constraint)
        csp_algorithm  = min_conflicts
        answer         = csp_algorithm(csp_problem, **kargs)
        nassigns       = csp_problem.nassigns

        # clean up the answer: it will be a dictionary of {service_name:boot_order},
        #  but boot_orders may be duplicated and it may not be in order.
        answer = answer.items()
        answer.sort(lambda x,y: cmp(x[1], y[1]))
        return [ x[0] for x in answer ]


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
