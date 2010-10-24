""" cortex.core.util
"""

def all_in(path,files):
    """ returns True if the given path has every file mentioned """
    assert isinstance(files,list),"expected list would be passed in"
    tmp = os.listdir(path)
    for f in files:
        if f not in tmp:
            return False
    return True

def is_venv(path):
    """ assumes path exists """
    dirs = 'bin include lib'
    return all_in(path, dirs.split())

def has_node_layout(path):
    """ TODO: fill out stub
    """
    return True

def path_is_cortex_node(path):
    """
    """
    assert os.path.exists(path),"Since you passed a string I thought it was a directory.. does not even exist"
    return is_venv(path) and has_node_layout(path)

def host_is_cortex_node(dct):
    """ answer whether the dictionary corresponds to a listening node
        TODO: fill out stub
    """
    addr = dct['addr']
    port = dct['port']
    return True

def is_cortex_node(other):
    """ answer whether <generic> is a cortex node """
    if isinstance(other,str):
        return path_is_cortex_node(other)
    else:
        return host_is_cortex_node(other)
