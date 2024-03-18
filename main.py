import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import sys

import auxiliar_methods as funcs
import layouts as lyts

import grandalf
from grandalf.layouts import SugiyamaLayout

import matplotlib.pyplot as plt


reactions = []

def main():

    G = nx.DiGraph()    

    reactions, components = funcs.read_graph(G)

    isConnected = funcs.isConnected(G)

    S = nx.Graph()
    if not isConnected:
        H = G.to_undirected()
        S = [G.subgraph(c).copy() for c in nx.connected_components(H)]
    
    G = S
    funcs.removeCyclesByNodeInMostCycles(G)
    funcs.changeSourceAndSinkNodeType(G)

    colors = funcs.setColorNodeType(G)
    
    sugiyama(colors)
   

def sugiyama(colors):

    g = grandalf.utils.convert_nextworkx_graph_to_grandalf(G)


    class defaultview(object):
        w, h = 20, 20


    for v in g.C[0].sV:
        v.view = defaultview()

    sug = SugiyamaLayout(g.C[0])
    sug.init_all()  # roots = [V[0]])
    sug.draw()  # Calculate positions

    poses = {v.data: (v.view.xy[0], v.view.xy[1]) for v in g.C[0].sV}  # Extract positions

    funcs.rearangeSources(G, poses)
    funcs.countCrossings(G,poses)

    nx.draw(G, pos=poses, with_labels=True, node_color=colors)
    
    plt.show()

    # nt = Network(directed=True)
    # nt.from_nx(G)
    # nt.show_buttons(filter_=['layout'])
    # nt.show('nx.html', notebook=False)

if __name__ == "__main__":
    main()