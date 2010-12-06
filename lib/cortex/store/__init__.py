""" cortex.store.__init__
"""

"""
    Scratchpad:
        class HierarchicalWrapper(HierarchicalData):
           """ """
           def __init__(self, proxy_name):
               super(HierarchicalWrapper,self).__init__()
               self._proxy = proxy_name

           def __getattr__(self, name):
               """ """
               if hasattr(self, '_proxy') and hasattr(self._proxy, name):
                   return getattr(object.__getattribute__(self,'_proxy'), name)
               else:
                   return super(HierarchicalWrapper,self).__getattr__(name)

"""
