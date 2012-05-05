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

def classtree(cls, indent=0, out='', base_url='', pfx=[]):
    cname = cls.__name__
    if cname=='object': return ''
    link = '<a class="adepth_{0}" href="{1}">{2}</a>'
    link = link.format(indent, '/'.join(map(str, pfx)), cname)
    out += ('<br/>' if indent else '') + '.'*indent + ' ' + link
    for supercls in cls.__bases__:
        rellink  = base_url + ('/__class__/' if not indent else '')
        rellink += '__bases__[{0}]'.format(cls.__bases__.index(supercls))
        out += classtree(supercls, indent+1, pfx=pfx + [rellink])
    return out
