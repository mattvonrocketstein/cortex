""" cortex.core.helpers
"""
import os

from cortex.core.data import SERVICES_DOTPATH

class shell:
    """a dumb abstraction for a shell rooted at <path>"""
    def __init__(self, path):
        self.path = path

    def __call__(self, line, quiet=False):
        """ """
        os.system('cd "'+path+'"; '+line)

def get_mod(mod_name, root_dotpath=SERVICES_DOTPATH):
    """ stupid helper to snag modules from inside the services root """
    out = {}
    ns  = {}
    exec('from ' + root_dotpath + ' import ' + mod_name + ' as mod', ns)
    mod = ns['mod']

    for name in dir(mod):
        val = getattr(mod, name)
        out[name] = val
    return out

def getAnswer(Q, yesAction=None, noAction=None, dispatcher=None):
    """ getAnswer: ask a "yes or no" question, dispatch to an action
        (possibly the empty-action) based on user-response on stdin

          Some Shortcuts w/ Questions:
             <Q> will be given a question mark if it doesn't have one,
             <Q> capitalization will be formulated as if a book title
    """
    ans = "JUNK_DATA"
    if not Q.endswith('?'): Q += '?'
    question = Q.title()
    question+=' [y/n] > '
    while ans not in 'ynYN':
        ans = raw_input(question)
    if ans.lower()=='y':   ans = True;  result = yesAction and yesAction()
    elif ans.lower()=='n': ans = False; result = noAction and noAction()
    return ans,result
