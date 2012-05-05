"""
"""
from cortex.core.util import report
from cortex.util.pyack import pyack

from xgoogle.search import GoogleSearch, SearchError
def search_with_google(search=None, _id=None, **kargs):
    class Results(list):
        pass

    try:
        gs = GoogleSearch(search)
        gs.results_per_page = 50
        results = gs.get_results()
        results = [ dict(title=res.title.encode('utf8'),
                         description=res.desc.encode('utf8'),
                         url=res.url.encode('utf8')) for res in results ]
        Results = Results(results)
        Results.weighted = results
        Results.id = _id
        Results.gs = gs
        return Results
    except SearchError, e:
        report("Search failed: %s" % e)



def search_with_ack(wd=None, search=None, _id=None):
    """ """
    acker = pyack('{search} {dir}'.format(search=search, dir=wd))
    acker();
    acker.id = _id
    return acker
