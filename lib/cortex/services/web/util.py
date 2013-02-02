""" cortex.services.web.util
"""

from urllib import urlencode as urlenc

from goulash.util import uniq
from cortex.core.util import report

class Multiplot(object):
    registry = {}

    def __init__(self, webroot):
        self.subplots = {}
        self.endpoint_root = '/'
        self._multiplot_url = '/_multiplot'
        self.short_url_root = '/multiplot'
        self.web = webroot
        self.uuid = uniq()
        Multiplot.registry[self.uuid] = self

    def install_subplot(self, name, data_generator):
        """ """
        name = name.replace('.', '_').replace(' ','_')
        self.subplots[name] = data_generator

    def install_streams(self):
        for name,data_generator in self.subplots.items():
            self.web.make_data_stream(name, data_generator)

    @property
    def shorturl(self):
        return self.short_url_root + '/'+self.uuid

    @property
    def wrapped_url(self):
        return self._url(self.short_url_root + '?')

    @property
    def url(self):
        """ full ajax url """
        return self._url(self.short_url_root + '?')

    def _url(self, full_url):
        for name in self.subplots:
            full_url += '&' + \
                        urlenc(dict(endpoint=self.endpoint_root + name,
                                    title=name))
        return full_url

def draw_ugraph(k, fname, report):
    """ actually build a graph

          #A.graph_attr['label']='known universe topology'
          #nx.draw_random(G) #nx.draw_circular(G)
          #nx.draw_graphviz(G) #nx.write_dot(G,'file.dot')
          #nx.draw(A) #nx.draw_random(G) #nx.draw_spectral(G)

    """
    import networkx as nx
    from pygraphviz import *
    G = nx.Graph()
    G.add_edges_from(k)
    A=nx.to_agraph(G)
    H = nx.from_agraph(A)
    A.edge_attr['color']='red'
    A.layout()
    A.draw(fname)
