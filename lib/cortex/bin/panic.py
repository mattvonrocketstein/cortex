#!/usr/bin/env python
import os
import psutil

def entry():
    """ think about it.. this is not cortex --panic for a good reason."""
    print '-'*80
    procs = [x for x in psutil.process_iter() if 'cortex' in x.name]
    print procs
    pids = [x.pid for x in procs]
    [ os.system('kill -KILL {0}'.format(pid)) for pid in pids ]
    return
