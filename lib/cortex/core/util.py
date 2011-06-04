""" cortex.core.util
"""
from cortex.core.data import SERVICES_DOTPATH

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

# Patterns in reporting
####################################################################
import sys, inspect

import pygments
from pygments import highlight
from pygments.lexers import PythonLexer, PythonTracebackLexer
from pygments.formatters import HtmlFormatter,Terminal256Formatter
from IPython.ColorANSI import TermColors

# Pygments data
plex  = PythonLexer()
tblex = PythonTracebackLexer()
hfom  = HtmlFormatter()
hfom2 = HtmlFormatter(cssclass="autumn")
colorize  = lambda code: highlight(code, plex, hfom)
colorize2 = lambda code: highlight(code, plex, hfom2)

class console:
    """ """
    def __getattr__(self,name):
        x = getattr(TermColors, name.title(),None)
        if x!=None:
            def func(string,_print=False):
                z = x + string + TermColors.Normal
                if _print:
                    print z
                return z
            return func
        else:
            raise AttributeError,name

    def vertical_space(self):
        print

    @staticmethod
    def blue(string):
        """ TODO: generic function for this
        """
        return TermColors.Blue + string + TermColors.Normal
    @staticmethod
    def colortb(string):
        return highlight(string, tblex, Terminal256Formatter())

    @staticmethod
    def color(string):
        return highlight(string, plex, Terminal256Formatter())

    @staticmethod
    def draw_line(msg='', length=80, display=True):
        if msg and not msg.startswith(' '): msg = ' '+msg
        if msg and not msg.endswith(' '):   msg = msg+' '
        rlength = length - len(msg)
        out = '-' * (rlength/2)
        out+= msg + out
        out = TermColors.Red+ out + TermColors.Normal
        if display:
            print out
        return out
console=console()

import time
import uuid
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
    self = flocals.get('self',None)
    kls  = self and self.__class__
    func = self and getattr(self,func_name)
    return dict(file=file_name,
                kls=kls,
                self=self,
                func=func,
                func_name=func_name)

def whosdaddy():
    """ displays information about the caller's caller """
    # if self is a named argument in the locals, print
    # the class name, otherwise admit that we don't know
    caller_info = getcaller(3)
    kls         = caller_info['kls']
    file_name   = caller_info['file']
    func_name   = caller_info['func_name']
    header = (kls and kls.__name__) or '<??>'
    header = ' ' + header + '.' + func_name
    return ' + in ' + file_name + '\n  ' + header + ' --'

def report(*args, **kargs):
    """ the global reporting mechanism.

          TODO: clean this up and allow subscribers like
               <log>, <syndicate>,  and <call-your-moms-cell-phone>.
    """
    global console
    import sys
    stream = kargs.get('stream', sys.stdout)
    header = kargs.get('header', None)
    full = False
    if header is None: header=whosdaddy(); full=True
    print header
    if full:
        stream.write( '\targs='+console.color(str(args))+       '\tkargs=')
        flush = kargs.pop('flush', False)
        stream.write(console.color(str(kargs)))

    #if flush:
    #    sys.stdout.flush() # is this even working with ipython?

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
