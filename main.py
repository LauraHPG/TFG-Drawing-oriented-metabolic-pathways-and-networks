
import networkx as nx
from pyvis.network import Network
import sys

import auxiliar_methods as funcs
import layouts as lyts

import matplotlib.pyplot as plt


G = nx.DiGraph()    
reactions = []
poses = {}

def main():

    reactions, components = funcs.read_graph(G)

    funcs.isConnected(G)
    
    funcs.removeCyclesByNodeInMostCycles(G)
    result = funcs.getLargestCC(G)

    if result == -1: # 1 CC

        funcs.changeSourceAndSinkNodeType(G)

        colors = funcs.setColorNodeType(G)
        
        poses = funcs.sugiyama(G)
        

    else: # largest CC

        funcs.changeSourceAndSinkNodeType(result)

        colors = funcs.setColorNodeType(result)
        
        poses = funcs.sugiyama(result)
    

    funcs.rearangeSources(G, poses)
    funcs.countCrossings(G,poses)

    nx.draw(G, pos=poses, with_labels=True, node_color=colors)
    
    plt.show()

    # nt = Network(directed=True)
    # nt.from_nx(graph)
    # nt.show_buttons(filter_=['layout'])
    # nt.show('nx.html', notebook=False)

if __name__ == "__main__":
    main()