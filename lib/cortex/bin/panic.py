#!/usr/bin/env python
import os
import psutil

def entry():
    """ think about it.. this is not cortex --panic for a good reason."""
    print '-'*80
    procs = [x for x in psutil.process_iter() if 'cortex' in x.name]
    print procs
    return [x.kill() for x in procs]
