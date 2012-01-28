#!/usr/bin/env python
import os

def entry():
    print '-'*80
    _procs = "ps aux|grep {user}|grep python|grep cortex"
    _procs = _procs.format(user=os.environ['USER'])
    procs = os.popen(_procs).read()
    print procs
    print '-'*80
    pids =  os.popen(_procs+"|awk '{print $2}'").read().split()
    print pids
    _pids = ' '.join(pids)
    print os.popen('kill -KILL '+_pids).read()
