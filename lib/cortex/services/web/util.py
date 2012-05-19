""" cortex.services.web.util
"""

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

def ugraph(universe):
    """ builds an adjacency matrix for the universe topology:
        a list of tuples where every tuple is parent -> child

        TODO: a real traversal for arbitrary depth
    """
    stuff = universe.children() + [universe]
    stuff = [ [x, x.children()] for x in stuff if hasattr(x, 'children') ]
    stuff = dict(stuff)
    name = lambda q: q.name if q!=universe else 'universe'
    out = []
    for node, children in stuff.items():
        for z in children:
            out.append( (name(node), name(z)) )
    return out
