""" cortex.util.__init__
"""

from cortex.util.namespaces import Namespace

class Memoize:
    """
         taken from: http://snippets.dzone.com/posts/show/4840
    """
    def __init__ (self, f):
        self.f = f
        self.mem = {}
    def __call__ (self, *args, **kwargs):
        if (args, str(kwargs)) in self.mem:
            return self.mem[args, str(kwargs)]
        else:
            tmp = self.f(*args, **kwargs)
            self.mem[args, str(kwargs)] = tmp
            return tmp
