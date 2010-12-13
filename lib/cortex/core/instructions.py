""" cortex.core.instructions
"""

from cortex.core.util import report

class Instruction(object):
    def syntax(*args, **kargs):
        pass
    def semantics(*args, **kargs):
        pass

class InstructionSet(object):
    """ builder for structured lists """
    def __init__(self):
        self.instructionset = []

    def append(self, other):
        return self.instructionset.append(other)

    def records_result_locally(name):
        """ builds a decorator to  """
        def dec(fxn):
            def new_fxn(*args, **kargs):
                """ the replacement function """
                result  = fxn(*args, **kargs)
                himself = args[0]
                getattr(himself, name).append(result)
                return result
            return new_fxn
        return dec

    def finish(self):
        """ call when this instructionset is complete """
        from cortex.core.api import publish
        do = publish()['do']
        do([x for x in self.instructionset])

    @records_result_locally('instructionset')
    def build_agent(self, name='', kls=None, **kls_kargs):
        """ instruction for building an agent """
        return [ 'build_agent',
                 (name,),
                 dict(kls=kls, kls_kargs=kls_kargs) ]

    @records_result_locally('instructionset')
    def load_service(self, name, **kargs):
        """ instruction for loading a service """
        return [ "load_service",
                 (name,),
                 kargs  ]
