""" cortex.services.web.resource.util
"""
def alligator2paren(obj):
    return str(obj).replace('<','(').replace('>',')')

def get_source(obj):
    import inspect
    from cortex.core.hds import HDS
    if obj==type or isinstance(obj, HDS):
        return 'Could not retrieve source.'
    try:
        return inspect.getsource(obj)
    except:
        return get_source(getattr(obj, 'im_func', obj.__class__))
