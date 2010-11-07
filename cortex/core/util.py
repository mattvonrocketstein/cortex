""" cortex.core.util
"""

# Patterns in reporting
####################################################################
import inspect

import pygments
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter,Terminal256Formatter
from IPython.ColorANSI import TermColors

#from django.core.management.color import color_style
# Style and style helpers
#style = color_style()
#yellow = style.HTTP_NOT_FOUND

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
    """ """
    return inspect.stack()[1][3]

def whosdaddy():
    """ """
    x = inspect.stack()[2]
    frame = x[0]
    fname = x[1]
    flocals = frame.f_locals
    func_name = x[3]
    if 'self' in flocals:
        header = flocals['self'].__class__.__name__
    else:
        header='<??>'
    header = header+'.'+func_name
    print ' + ', fname, '\n  ', header,'--'

def report(*args, **kargs):
    """ """
    global console
    whosdaddy()
    print '\targs=',
    print console.color(str(args)),
    print '\tkargs=',
    console.color(str(kargs))

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
