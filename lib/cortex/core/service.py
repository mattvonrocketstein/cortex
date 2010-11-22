""" cortex.core.service
"""

from cortex.core.node import Node
from cortex.core.manager import Manager
from cortex.core.util import report, console
from cortex.core.ground import HierarchicalWrapper, HierarchicalData
from cortex.contrib.aima.csp import CSP, AC3, min_conflicts, backtracking_search
from cortex.core.data import NOOP

class ServiceManager(Manager):
    """ ServiceManager exists mainly to make universe.services obey list
        and dictionary api simultaneously.  Additionally, it provides a
        commonly used Exception.
    """

    # Class specifying how the objects in this
    #  container will be represented
    asset_class = HierarchicalData

    def items(self):
        """ dictionary compatability """
        return [[var, val.service_obj] for var,val in Manager.items(self)]

    def __init__(self, *args, **kargs):
        """ """
        self.registry      = {}
        self._pending = []

        # TODO: when in doubt, autoproxy to..
        self.generic_store = HierarchicalWrapper('server_obj')

    def stop_all(self):
        """ stop all services this manager knows about """
        [ s.stop() for s in self ]

    # registering services can happen all the time..
    #  we don't want to do anything noisy here like write an event
    post_registration = NOOP

    #def register(self, name, **service_metadata):
    #    """ """
    #    return Manager.register(self, name, **service_metadata)

    def manage(self, name=None,fxn=None, fxn_kargs=None):
        """ queue up a pile of future assets and the arguments to
            initialize them with.  this pile will be dealt with when
            <load> is called.
        """
        self._pending.append([name, fxn, fxn_kargs])
        return name

    def load(self):
        """ if <manage> is used, this should be called after
            all calls to it are finished

            TODO: refactor
        """
        # Build table of start._boot_first constraints
        self.table = {}
        for item in self._pending:
                name, fxn, kargs = item
                self.table[name] = getattr(fxn.start, '_constraint_boot_first', [])

        ordering = self.resolve_boot_order()
        self.boot_order = ordering
        report('determined boot order:', ordering)
        for name in ordering:
            for item in self._pending:
                name2, fxn, fxn_kargs = item
                if name2 == name:
                        self.register(name, service_obj=fxn(**kargs).play(),
                                       boot_order=ordering.index(name),  kargs=kargs)

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
            if boot_order1 < boot_order2:
                first, second = s1, s2
            else:
               first, second = s2, s1

            # ensure the second isn't in the first's
            #  table of dependancies
            if second in self.table[first]: return False
            else: return True


    def labix_resolve_boot_order(self, **kargs):
        import constraint
        boot_order = constraint.Problem()
        for name, kls, ikargs in self._pending:
            boot_order.addVariables(name,range(len(self._pending)))
        boot_order.addConstraint(constraint.AllDifferentConstraint)
        def konstraint(*service_names):
            pass

    def resolve_boot_order(self, **kargs):
        """ TODO: try a different underlying CSP algorithm? it looks like
                  with some (inconsistent) initial conditions, and using
                  min-conflicts this can run for a num_steps:=very_large_number
                  before *proving* the system is inconsistent and giving up?

            NOTE: kargs will be passed on to the CSP-solving-algorithm that is chosen.
        """

        names = [x[0] for x in self._pending]
        # neighbors: every service participates in the constraints of the other self except itself
        neighbors = dict([ [service, [service2 for service2 in names if \
                                      service2!=service]] for service in names ])

        # vars: variables to solve over
        vars       = [ name for name in names ]

        # domains: every service could potentially be booted in any order
        domains     = dict([ [service, range(len(names))] for service in names])

        # the totality of the problem.  nothing to do with this now, but here it is.
        csp_definition = dict( vars = vars, domains = domains, neighbors = neighbors,
                               constraint = self._boot_order_constraint )
        # compute solution
        csp_problem    = CSP(vars, domains, neighbors, self._boot_order_constraint)
        csp_algorithm  = min_conflicts #backtracking_search #AC3 #
        answer         = csp_algorithm(csp_problem, **kargs)
        nassigns       = csp_problem.nassigns

        # clean up the answer: it will be a dictionary of {service_name:boot_order},
        #  but boot_order's may be duplicated, and it may not be in order.
        answer = answer.items()
        #raise Exception,answer
        answer.sort(lambda x,y: cmp(x[1], y[1]))
        #raise Exception, [x[0] for x in answer]
        return [ x[0] for x in answer ]


class Service(Node):
    """ abstractions representing a cortex service
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

# cheap singleton
SERVICES = ServiceManager()
