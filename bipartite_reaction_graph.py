# python3 bipartite_reaction_graph.py rn01100.lst
import matplotlib.pyplot as plt
import networkx as nx
from networkx import combinatorial_embedding_to_pos
import sys

reactions = []
components = set()

node_colors = {}

reaction_positions = {}
component_positions = {}

y_reactions = 0
y_components = 0

crossing_number = 0

G = nx.DiGraph()

for line in open(sys.argv[1]):
    reaction, substrates, products = line.rstrip().split(" : ")
    
    reactions.append(reaction)
    node_colors[reaction] = 'blue' 
    y_reactions += 1.75
    reaction_positions[reaction] = (y_reactions,2)

    for substrate in substrates.split(" "):

        G.add_edge(substrate, reaction)
        node_colors[substrate] = 'red'
        components.add(substrate)

        if not (substrate in component_positions):
            y_components += 1
            component_positions[substrate] = (y_components, 1)

        
    for product in products.split(" "):
        G.add_edge(reaction, product)
        node_colors[product] = 'red'
        components.add(product)

        if not (product in component_positions):
            y_components += 1
            component_positions[product] = (y_components, 1)


node_positions = {**reaction_positions,**component_positions}

def count_edge_crossings(graph, positions):
    crosses = 0
    for edge1 in G.edges():
        for edge2 in G.edges():
            if edge1 != edge2:

                node1 = edge1[0]
                node2 = edge1[1]
                node3 = edge2[0]
                node4 = edge2[1]

                r1_pos = 0
                c1_pos = 0
                r2_pos = 0
                c2_pos = 0

                if node1 in reactions:
                    r1_pos = reaction_positions[node1]
                    c1_pos = component_positions[node2]
                else:
                    r1_pos = reaction_positions[node2]
                    c1_pos = component_positions[node1]
                
                if node3 in reactions:
                    r2_pos = reaction_positions[node3]
                    c2_pos = component_positions[node4]
                else:
                    r2_pos = reaction_positions[node4]
                    c2_pos = component_positions[node3]
                
                if r1_pos < r2_pos and c1_pos > c2_pos:
                    crosses += 1
                elif r2_pos < r1_pos and c2_pos > c1_pos:
                    crosses += 1

    return crosses // 2


crossing_number = count_edge_crossings(G, node_positions)

print(f"Number of reactions: {reactions.__len__()}")
print(f"Number of components: {components.__len__()}")
print(f"Number of edges: {G.number_of_edges()}")
print(f"Number of edge crossings: {crossing_number}")

nx.draw(G, node_color=[node_colors[node] for node in G.nodes], pos=node_positions)

plt.show()

#######################
# Possible parameters #
#######################

# Total number of edge crossings --> minimize it
# Assing weight to the edges --> minimize max weight (subcase of previous ¿?)
