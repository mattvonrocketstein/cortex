""" cortex.core.util
"""
import inspect

from pprint import pprint
from StringIO import StringIO
from twisted.python.reflect import namedAny

# TODO: move some of this back into the real report lib
from report import report, console
def report_if_verbose(*args, **kargs):
    kargs['frames_back'] = 4
    from cortex import VERBOSE
    if VERBOSE:
        report(*args, **kargs)
report.console = console
from StringIO import StringIO
from pprint import pprint
def rpprint(obj,pad=' '*4):
    s = StringIO();
    pprint(obj,s);
    s.seek(0);
    report.console.draw_line('',display=False)
    print console.color('\n'.join(['\n']+map(lambda x: pad + x, s.read().split('\n'))))
report.pprint = rpprint

from cortex.core.data import SERVICES_DOTPATH

def rpprint(obj,pad=' '*4):
    s = StringIO();
    pprint(obj,s);
    s.seek(0);
    report.console.draw_line('',display=False)
    print console.color('\n'.join(['\n']+map(lambda x: pad + x, s.read().split('\n'))))
report.pprint = rpprint

def whoami():
    """ gives information about the caller """
    return inspect.stack()[1][3]

def getcaller(level=2):
    x = inspect.stack()[level]
    frame = x[0]
    file_name = x[1]
    flocals = frame.f_locals
    func_name = x[3]
    file = file_name
    self = flocals.pop('self', None)
    kls  = getattr(self, '__class__', None)
    func = getattr(self, func_name, None)
    return dict(file=file_name,
                kls=kls,
                locals=flocals,
                self=self,
                func=func,
                func_name=func_name)

# Patterns in files, directories
####################################################################

def all_in(path, files):
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

# Patterns in cortex
####################################################################

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

#
################################################################################

# TODO: register all locks with universe for debugging, etc
import threading
import multiprocessing
Lock = multiprocessing.Lock
Semaphore = threading.BoundedSemaphore

#
################################################################################

def alias(name):
    """ builds an alias for another attribute """
    @property
    def fxn(self):
        return getattr(self, name)

    return fxn

def service_is_stopped(name):
    """ returns a function of no arguments that
        if safe to be called periodically and knows
        whether the service corresponding to ``name``
        has halted
    """
    from cortex.core import api
    return lambda:  (api.universe|name).stopped

def pedigree(agent, names='iterate pause play setup start stop'):
    """ given an agent and some method names,
        returns which class the method names
        were defined in.
    """
    mro = agent.__class__.mro()
    names = names.split()
    results = {}
    for name in names:
        # knock out classes that dont even define the name
        candidates = [ kls for kls in mro if hasattr(kls, name)]
        # knock out classes where the name is defined but different/overridden
        candidates = [ kls for kls in candidates if \
                       getattr(kls, name) == getattr(agent.__class__, name) ]
        # take the last element, because it's the furthest away in the MRO
        if candidates: results[name] = candidates[-1]
        else: results[name] = None
    return results
