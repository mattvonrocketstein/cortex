"""
(automatically) reloading changed modules into a running program
From: Thomas Heller <thom...@ion-tof.com>
Thu, 15 Nov 2001 19:55:16 +0100

I wrote a script which
- automatically reloads changed modules depending on their timestamp
- updates existing objects in a running program: classes,
    functions, bound and unbound methods

The purpose is to speed up the development process, not to
update long running programs on the fly.

The script is not yet finished, however, I believe it is working.
Eventually I plan to submit it into the Python Cookbook.

I post it here to get early comments and suggestions for improvements.

Cheers,

Thomas

---- autoreload.py ----
"""
#
# autoreload.py - automatically reload changed source
# code into a running program
#
# You may want to place the following two lines
# into your sitecustomize.py:
#
# import autoreload
# autoreload.run()
#
# or you can use the superreload() function
# instead of the standard reload() function.
#

# Created: Thomas Heller, 2000-04-17
#
# $Id: autoreload.py,v 1.9 2001/11/15 18:41:18 thomas Exp $
#
# $Log: autoreload.py,v $
# Revision 1.9  2001/11/15 18:41:18  thomas
# Cleaned up and made working again before posting to c.l.p.
# Added code to update bound (or unbound) methods as suggested
# by Just van Rossum. Thanks!
#
# ...
#
# Revision 1.1  2001/10/04 16:54:04  thomas
# Discovered this old module on my machine, it didn't work too well,
# but seems worth to continue with it...
# Checked in as a first step.

version = "$Revision: 1.9 $".split()[1]

# ToDo:
#
#  Cannot reload __main__ - explain why this cannot work,
#  and explain a workaround.
#
#  Optimize - the number of watches objects (in old_objects)
#  grows without limits. Think if this is really necessary...


import time, os, threading, sys, types, imp

def _get_compiled_ext():
    for ext, mode, typ in imp.get_suffixes():
        if typ == imp.PY_COMPILED:
            return ext

# the official way to get the extension of compiled files (.pyc or .pyo)
PY_COMPILED_EXT = _get_compiled_ext()

class ModuleWatcher:
    running = 0
    def __init__(self):
        # If we don't do this, there may be tracebacks
        # when shutting down python.
        import atexit
        atexit.register(self.stop)

    def run(self):
        if self.running:
            print "# autoreload already running"
            return
        print "# starting autoreload"
        self.running = 1
        self.thread = threading.Thread(target=self._check_modules)
        self.thread.setDaemon(1)
        self.thread.start()

    def stop(self):
        if not self.running:
            #print "# autoreload not running"
            return
        self.running = 0
        self.thread.join()
        print "# autoreload stopped"

    def _check_modules(self):
        while self.running:
            time.sleep(1)
            for m in sys.modules.values():
                if not hasattr(m, '__file__'):
                    continue
                if m.__name__ == '__main__':

                    # we cannot reload(__main__) First I thought we
                    # could use mod = imp.load_module() and then
                    # reload(mod) to simulate reload(main), but this
                    # would execute the code in __main__ a second
                    # time.

                    continue
                file = m.__file__
                path, ext = os.path.splitext(file)

                if ext.lower() == '.py':
                    ext = PY_COMPILED_EXT
                    file = path + PY_COMPILED_EXT

                if ext != PY_COMPILED_EXT:
                    continue

                try:
                    if os.stat(file[:-1])[8] <= os.stat(file)[8]:
                        continue
                except OSError:
                    continue

                try:
                    print 'reloading module: ',m
                    superreload(m)
                except:
                    import traceback
                    traceback.print_exc(0)

def update_function(old, new, attrnames):
    for name in attrnames:
        setattr(old, name, getattr(new, name))

import gc
def update_class_t(old, new):
#    bfail=0
#    try:
#        old.__dict__.update
#    except AttributeError: # dictproxy?
#        try:
#            old.__dict__ = dict(old.__dict__)
#        except AttributeError:
#            print 'brutal fail',old
#            bfail=1
#            #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
#    if not bfail:
#        old.__dict__.update(new.__dict__)

    #
    old.__dict__.update(new.__dict__)
    refs = gc.get_referrers(old)
    #refs = [x for x in refs if type(ref) == types.ClassType]
    for ref in refs:
        if hasattr(ref, '__dict__'):
            for x,y in ref.__dict__.items():
                if ref.__dict__[x] == old:
                    print '{0}:{1}, '.format(ref,x),
                    ref.__dict__[x] = new

import inspect
def update_object(old_obj, new_obj):
    """ """
    #if inspect.isclass(new_obj):
    if type(new_obj) == types.ClassType:
        print 'class_t'
        update_class_t(old_obj, new_obj)
        return 1
    elif type(new_obj) == types.FunctionType:
        print 'func_t'
        update_function(old_obj,
                        new_obj,
                        "func_code func_defaults func_doc".split())
        return 1
    elif type(new_obj) == types.MethodType:
        print 'meth_t'
        update_function(old_obj.im_func,
                        new_obj.im_func,
                        "func_code func_defaults func_doc".split())
        return 1
    return 0

def superreload(module,
                reload=reload,
                _old_objects = {}):
    """superreload (module) -> module

    Enhanced version of the builtin reload function.
    superreload replaces the class dictionary of every top-level
    class in the module with the new one automatically,
    as well as every function's code object.
    """
    start = time.clock()
    # retrieve the attributes from the module before the reload,
    # and remember them in _old_objects.

    for name, object in module.__dict__.items():
        key = (module.__name__, name)
        _old_objects.setdefault(key, []).append(object)
        # print the refcount of old objects:
##        if type(object) in (types.FunctionType, types.ClassType):
##            print name, map(sys.getrefcount, _old_objects[key])

##    print "# reloading module %r" % module

    module = reload(module)
    # XXX We have a problem here if importing the module fails!

    # iterate over all objects and update them
    count = 0
    # XXX Can we optimize here?
    # It may be that no references to the objects are present
    # except those from our _old_objects dictionary.
    # We should remove those. I have to learn about weak-refs!
    for name, new_obj in module.__dict__.items():
        key = (module.__name__, name)
        print key
        if _old_objects.has_key(key):
            for old_obj in _old_objects[key]:
                count += update_object(old_obj, new_obj)

##    stop = time.clock()
##    print "# updated %d objects from %s" % (count, module)
##    print "# This took %.3f seconds" % (stop - start)

    return module

_watcher = ModuleWatcher()

run = _watcher.run
stop = _watcher.stop

__all__ = ['run', 'stop', 'superreload']
