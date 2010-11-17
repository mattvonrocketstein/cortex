""" cortex.core.util

      Scratch:

        import sys
        from IPython.Debugger import Pdb
        from IPython.Shell import IPShell
        from IPython import ipapi

        shell = IPShell(argv=[''])

        def set_trace():
            ip = ipapi.get()
            def_colors = ip.options.colors
            Pdb(def_colors).set_trace(sys._getframe().f_back)
"""


# Patterns in reporting
####################################################################
import sys, inspect

import pygments
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter,Terminal256Formatter
from IPython.ColorANSI import TermColors

# Pygments data
plex = PythonLexer()
hfom = HtmlFormatter()
hfom2 = HtmlFormatter(cssclass="autumn")
colorize = lambda code: highlight(code, plex, hfom)
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

    @staticmethod
    def blue(string):
        """ TODO: generic function for this
        """
        return TermColors.Blue + string + TermColors.Normal

    @staticmethod
    def color(string):
        return highlight(string, plex, Terminal256Formatter())

    @staticmethod
    def draw_line(length=80):
        #out = style.ERROR('-' * length)
        out = TermColor.Red+ '-' * length + TermColor.Normal
        print out
        return out
console=console()

def whoami():
    """ gives information about the caller """
    return inspect.stack()[1][3]

def whosdaddy():
    """ displays information about the caller's caller
    """
    x = inspect.stack()[2]
    frame = x[0]
    fname = x[1]
    flocals = frame.f_locals
    func_name = x[3]
    if 'self' in flocals:
        header = flocals['self'].__class__.__name__
    else:
        header = '<??>'
    header = header + '.' + func_name
    print ' + ', fname, '\n  ', header, '--'

def report(*args, **kargs):
    """ the global reporting mechanism.

          TODO: clean this up and allow subscribers like
               <log>, <syndicate>,  and <call-your-moms-cell-phone>.
    """
    global console
    whosdaddy()
    print '\targs=',
    print console.color(str(args)),
    print '\tkargs=',

    flush = kargs.pop('flush',False)
    console.color(str(kargs))

    #if flush:
    #    sys.stdout.flush() # is this even working with ipython?

# Patterns in files, directories
####################################################################

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

# Misc Patterns
####################################################################
"""
try:
    import pynotify
except ImportError:
    report("you don't seem to have pynotify installed")
else:
    if pynotify.init("Cortex"):
        def notifier(header, stuff):
            n = pynotify.Notification(header,stuff)
            #n = pynotify.Notification("Cortex started", "stuff")
            #n.set_urgency(pynotify.URGENCY_LOW)
            #n.set_urgency(pynotify.URGENCY_NORMAL)
            n.set_urgency(pynotify.URGENCY_CRITICAL)
            n.set_timeout(1000)
            n.show()
    else:
        def notifier(header,stuff):
            report("NOTIFIER: ",header,stuff)
        print "there was a problem initializing the pynotify module"
"""
