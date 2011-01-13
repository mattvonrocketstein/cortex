""" cortex.tests.hds
       tests cortex.contrib.hds, your friendly neighborhood
       hierarchical data structure pattern.

       TODO: NIY
"""

def test():
    """ """
    model=HierarchicalData()

    # model.person is contstruted on the fly:
    model.person.surname = "uwe"
    model.person.name = "schmitt"
    model.number = 1

    print; print "access via attributes:"; print
    print "model.person.surname=", model.person.surname
    print "model.person.name=", model.person.name
    print "model.number=", model.number; print

    print "print complete model:"; print
    print model; print
    o = pickle.loads(pickle.dumps(model))
    print "unpickle after pickle:"; print; print o; print
    print "paths from root to leaves and values at leaves:"
    print; print getLeaves(o)

if __name__=="__main__":
    test()
