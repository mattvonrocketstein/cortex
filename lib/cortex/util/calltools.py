""" calltools
"""

class callchain(object):
    def __init__(self, chain):
        self.chain = chain

    def __str__(self):
        return 'call-chain: '+str([x.__name__ for x in self.chain])

    def __call__(self, *args, **kargs):
        results = [x(*args, **kargs) for x in self.chain]
        return results[-1]
