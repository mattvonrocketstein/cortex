""" cortex.util.decorators.multimethods
     GVRs pattern modified for instance methods,
      where the last registered type-map always wins.

     Adapted from:
       http://www.artima.com/weblogs/viewpost.jsp?thread=101605
"""

registry = {}

class MultiMethod(object):
    """ """
    def __str__(self):
        return '<MultiMethod "{mm}": {N} choices'.format(mm=self.name,
                                                      N=len(self.typemap))+">"
    def __init__(self, name):
        self.name = name
        self.typemap = {}
    def register(self, types, function):
        #if types in self.typemap and self.typemap[types]!=function:
        #    #raise TypeError("duplicate registration: "+str([self.typemap[types].__doc__,function.__doc__]))
        #    raise TypeError("duplicate registration: "+str([self.typemap[types].func_code,function.func_code]))
        self.typemap[types] = function

def multimethod(*types):
    def register(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        def fxn(*args, **kargs):
            himself=args[0]
            args=args[1:]
            this_map = tuple(map(type,args[1:]))
            if len(this_map)!=len(args[1:]):
                raise TypeError,"Lengths differ! "+str( [this_map, args] )
            choice = registry[name].typemap.get( this_map)
            if choice==None:
                for choice in registry[name].typemap:
                    #print 'checking choice with',args,choice
                    maybe_no = [ not isinstance(args[i], choice[i]) for i in range(len(args)) ]
                    if not any(maybe_no): # all true
                        choice = registry[name].typemap.get( choice )
                        return choice(himself, *args, **kargs)
                raise TypeError,"Could not even map with isinstance"

            return choice(*args, **kargs)
        return fxn

    return register

if __name__=="__main__":
    from cortex.util.types import NonString
    class test:
        @multimethod(NonString)
        def test(self, x):
            """ i m"""
            print 'int',x
        @multimethod(str)
        def test(self, x):
            """ str m"""
            print 'str',x

    test().test(1)
    test().test('2')
