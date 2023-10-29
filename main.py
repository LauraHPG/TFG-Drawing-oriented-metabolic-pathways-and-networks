import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import sys

import auxiliar_methods as funcs
import layouts as lyts
import hill_climbing as hc

def main():
    G = nx.DiGraph()

    reactions, components = funcs.read_graph(G)

    node_colors = {node: funcs.get_color(data['node_type']) for node, data in G.nodes(data=True)}
    nx.set_node_attributes(G, node_colors, 'color')

    colors = [data['color'] for _, data in G.nodes(data=True)]

    pos = lyts.selectInitialLayout(G)

    if pos == None:
        print("Please, select valid layout")
        return

    n_crossings, _ = funcs.count_edge_crossings(G, pos, reactions)
    print(f"Initial number of crossings: {n_crossings}")

    # subax1 = plt.subplot(131)    
    # nx.draw(G, pos, node_color=colors)

    pos = funcs.split_components_1(G,pos,components)
    n_crossings, _ = funcs.count_edge_crossings(G, pos, reactions)

    print(f"Number of crossings split components: {n_crossings}")

    # subax3 = plt.subplot(132)
    # nx.draw(G, pos, node_color=colors)

    pos = funcs.split_reactions_1(G,pos,reactions)
    n_crossings, _ = funcs.count_edge_crossings(G, pos, reactions)

    print(f"Number of crossings split reactions: {n_crossings}")

    print(f"Final number of crossings: {n_crossings}")
    
    # subax3 = plt.subplot(133)

    pos = funcs.rearange_positions(pos)

    nx.draw(G, pos, node_color=colors)

    plt.show()

if __name__ == "__main__":
    main()