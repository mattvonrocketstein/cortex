""" cortex.services.manager
"""
from collections import defaultdict
from cortex.core.agent.manager import AgentManager,Manager
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
