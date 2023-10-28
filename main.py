import matplotlib.pyplot as plt
import networkx as nx
from networkx import combinatorial_embedding_to_pos
import sys

import auxiliar_methods as funcs
import layouts as lyts

def main():
    G = nx.DiGraph()
    reactions = {}
    components = {}

    reactions = funcs.read_graph(G)

    node_colors = {node: funcs.get_color(data['node_type']) for node, data in G.nodes(data=True)}
    nx.set_node_attributes(G, node_colors, 'color')

    colors = [data['color'] for _, data in G.nodes(data=True)]

    pos = lyts.selectInitialLayout(G)

    if pos == None:
        print("Please, select valid layout")
        return

    print(f"Number of crossings: {funcs.count_edge_crossings(G, pos, reactions)}")

    nx.draw(G, pos, node_color=colors)
    plt.show()

if __name__ == "__main__":
    main()