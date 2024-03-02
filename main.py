import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import sys

import auxiliar_methods as funcs
import layouts as lyts
import hill_climbing as hc


import grandalf
from grandalf.layouts import SugiyamaLayout

import matplotlib.pyplot as plt


G = nx.DiGraph()
reactions = []
# colors = []

def main():

    reactions, components = funcs.read_graph(G)

    funcs.removeCyclesByNodeInMostCycles(G)
    funcs.splitHighDegreeComponents(G)
    funcs.changeSourceAndSinkNodeType(G)

    node_colors = {node: funcs.get_color(data['node_type']) for node, data in G.nodes(data=True)}
    nx.set_node_attributes(G, node_colors, 'color')

    colors = [data['color'] for _, data in G.nodes(data=True)]


    mode = input("Select mode:\n     1: Lau\n     2: Sugiyama\n     3: DAG\n     4: CCs\n")
    match mode:
        case "1": 
            lau(colors)
        case "2":
            sugiyama(colors)
        case "3":
            dag(colors)
        case "4":
            connectedComponents(colors)

def lau(colors):        
    pos = lyts.selectInitialLayout(G)

    if pos == None:
        print("Please, select valid layout")
        return

    n_crossings, _ = funcs.count_edge_crossings(G, pos, reactions)
    print(f"Initial number of crossings: {n_crossings}")

    # subax1 = plt.subplot(131)    
    # nx.draw(G, pos, node_color=colors)

    # pos = funcs.splitNodesIntoDifferentLayers(G, components, reactions, pos)
    n_crossings, _ = funcs.count_edge_crossings(G, pos, reactions)

    print(f"Final number of crossings: {n_crossings}")

    source, sink = funcs.get_source_and_sink_nodes(G)

    print(f"Number of source nodes: {len(source)}")
    # print(source)
    print(f"Number of sink nodes: {len(sink)}")
    # print(sink)
    # subax3 = plt.subplot(133)

    pos = funcs.rearange_positions(pos)

    nx.draw(G, pos, node_color=colors)
    # nx.draw(G, pos=nx.spring_layout(G))  
    plt.show()

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

    nx.draw(G, pos=poses, with_labels=True, node_color=colors)
    
    plt.show()

def dag(colors):
    for layer, nodes in enumerate(nx.topological_generations(G)):
        # `multipartite_layout` expects the layer as a node attribute, so add the
        # numeric layer value as a node attribute
        for node in nodes:
            G.nodes[node]["layer"] = layer

    # Compute the multipartite_layout using the "layer" node attribute
    pos = nx.multipartite_layout(G, subset_key="layer")

    fig, ax = plt.subplots()
    nx.draw_networkx(G, pos=pos, ax=ax, node_color=colors)
    ax.set_title("DAG layout in topological order")
    fig.tight_layout()
    plt.show()


def connectedComponents(colors):
    H = G.to_undirected()
    S = [H.subgraph(c).copy() for c in nx.connected_components(H)]
    for subGraph in S:
        nx.draw(subGraph, with_labels=True)
        plt.show()
    
if __name__ == "__main__":
    main()