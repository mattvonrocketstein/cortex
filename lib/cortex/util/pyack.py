""" pyack

    a dumb interface for getting ack data into python

    USAGE:

      call it with a given search string or directory
         >>> z = pyack('search_string')
         >>> z = pyack('search_string directory')
         >>> z = pyack('search_string directory --whatever-ack-args')
         >>> z()

      number of matching files:
         >>> len(z) #
         291

      list of matching files
         >>> z.files

      matching line-no's for a given file. (lineno's are strings):
         >>> z[filename]
         [..,]
"""

import os
from collections import defaultdict

def which(name):
    return os.popen('which '+name).readlines()[0].strip()

class pyack(object):
    """ thin wrapper on ack to get some of the data into python
    """

    def __init__(self, call_string):
        self.call_string = call_string
        self.record = defaultdict(lambda:defaultdict(lambda:[]))

    def __len__(self):
        """ """
        return len(self.files)

    def __getitem__(self, key):
        """ given a file, returns matching lines """
        return self.record[key].keys()

    def __call__(self):
        """
            construct self.records such that it looks like
            {file: {lineno:match} }
        """
        cmd = which('ack') + ' ' + self.call_string
        p = os.popen(cmd)
        for x in iter(p.readline, ''):
            if not x: continue
            i1 = x.find(':')
            i2 = x.find(':',i1+1)+1
            match = x[i2:]
            _file = x[:i1]
            lineno = x[i1+1:i2-1]
            self.record[_file][lineno]=match

    @property
    def weighted(self):
        return [x for x in reversed(sorted([ [len(self.record[r]),r] for r in self.record ]))]

    @property
    def files(self):
        """ returns matching files """
        return self.record.keys()
