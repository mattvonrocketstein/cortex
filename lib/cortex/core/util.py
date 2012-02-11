""" cortex.core.util
"""
import inspect
import time, uuid

# TODO: move some of this back into the real report lib
from report import report, console
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

from StringIO import StringIO
from pprint import pprint

from cortex.core.data import SERVICES_DOTPATH

def rpprint(obj,pad=' '*4):
    s = StringIO();
    pprint(obj,s);
    s.seek(0);
    report.console.draw_line('',display=False)
    print console.color('\n'.join(['\n']+map(lambda x: pad + x, s.read().split('\n'))))
report.pprint = rpprint

def get_mod(mod_name, root_dotpath=SERVICES_DOTPATH):
    """ stupid helper for universe to snag modules
        from inside the services root """
    from twisted.python.reflect import namedAny
    mod = namedAny('.'.join([root_dotpath,mod_name]))
    out = {}
    ns  = {}
    #exec('from ' + root_dotpath + ' import ' + mod_name + ' as mod', ns)
    #mod = ns['mod']

    for name in dir(mod):
        val = getattr(mod, name)
        out[name] = val
    return out

def uniq():
    return str(uuid.uuid1()).split('-')[0]+str(time.time())[:-3]

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
    kls  = self and self.__class__
    func = self and getattr(self, func_name)
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

class classproperty(property):
    """
    class A (object):

        _foo = 1

        @classproperty
        @classmethod
        def foo(cls):
            return cls._foo

        @foo.setter
        @classmethod
        def foo(cls, value):
            cls.foo = value
    """

    def __get__(self, obj, type_):
        return self.fget.__get__(None, type_)()

    def __set__(self, obj, value):
        cls = type(obj)
        return self.fset.__get__(None, cls)(value)


#
################################################################################

# TODO: register all locks with universe for debugging, etc
import threading
import multiprocessing
Lock = multiprocessing.Lock
Semaphore = threading.BoundedSemaphore

#
################################################################################

from inspect import ismethod, isclass
def isclassmethod( m ):
    return ismethod(m) and isclass(m.__self__)

#
################################################################################

def alias(name):
    """ builds an named alias for another attribute """
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


def uuid():
    import uuid
    return str(uuid.uuid1())
