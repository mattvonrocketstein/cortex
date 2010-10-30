
import os
print '-'*80
_procs = "ps aux|grep matt|grep python|grep -v stat|grep -v grep|grep -v pbat|grep -v wic"
procs = os.popen(_procs).read()
print procs
print '-'*80
pids =  os.popen(_procs+"|awk '{print $2}'").read().split()
print pids
_pids = ' '.join(pids)
print os.popen('kill -KILL '+_pids).read()

