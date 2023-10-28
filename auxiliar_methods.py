import networkx as nx
import sys

def edges_cross_1D(r1,r2,c1,c2):
    return (r1 < r2 and c1 > c2) or (r2 < r1 and c2 > c1)

def determinant(px,py,qx,qy,rx,ry):
	return ((qx-px)*(ry-py) - (rx-px)*(qy-py))

def edges_cross_2D(r1,r2,c1,c2):
    d_e1_e2_1 = determinant(r1[0],r1[1],c1[0],c1[1],r2[0],r2[1])
    d_e1_e2_2 = determinant(r1[0],r1[1],c1[0],c1[1],c2[0],c2[1])

    d_e2_e1_1 = determinant(r2[0],r2[1],c2[0],c2[1],r1[0],r1[1])
    d_e2_e1_2 = determinant(r2[0],r2[1],c2[0],c2[1],c1[0],c1[1])


    return d_e1_e2_1*d_e1_e2_2 < 0 and d_e2_e1_1*d_e2_e1_2 < 0

def count_edge_crossings(graph, positions, reactions):
    crosses = 0
    for edge1 in graph.edges():
        for edge2 in graph.edges():
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
                    r1_pos = positions[node1]
                    c1_pos = positions[node2]
                else:
                    r1_pos = positions[node2]
                    c1_pos = positions[node1]
                
                if node3 in reactions:
                    r2_pos = positions[node3]
                    c2_pos = positions[node4]
                else:
                    r2_pos = positions[node4]
                    c2_pos = positions[node3]
                
                if edges_cross_1D(r1_pos[0],r2_pos[0],c1_pos[0],c2_pos[0]):
                    crosses += 1


    return crosses // 2

def read_graph(graph):
    reactions = []
    nx.set_node_attributes(graph, {})
    for line in open(sys.argv[1]):
        reaction, substrates, products = line.rstrip().split(" : ")
        
        graph.add_node(reaction, node_type='reaction')
        reactions.append(graph.nodes[reaction])

        for substrate in substrates.split(" "):

            graph.add_edge(substrate, reaction)
            graph.add_node(substrate, node_type='component')

            
        for product in products.split(" "):
            graph.add_edge(reaction, product)
            graph.add_node(product, node_type='component')

    return [node for node, data in graph.nodes(data=True) if data['node_type'] == 'reaction']

def get_color(node_type):
    if node_type == 'reaction':
        return 'blue'
    else:
        return 'red'
    
def nodes_ordered_by_degree(graph, nodes=None):
    """
    Returns a list of nodes ordered by degree in descending order.

    Args:
    graph (networkx.Graph): The input graph.
    nodes (list or None): List of nodes to order by degree. If None, all nodes in the graph are used.

    Returns:
    list: A list of nodes ordered by degree in descending order.
    """
    if nodes is None:
        nodes = graph.nodes()

    # Calculate the degree for each node and create a list of (node, degree) tuples
    degree_list = [(node, degree) for node, degree in graph.degree(nodes)]

    # Sort the list by degree in descending order
    degree_list.sort(key=lambda x: x[1], reverse=True)

    # Extract the nodes from the sorted list
    nodes_sorted_by_degree = [node for node, _ in degree_list]

    return nodes_sorted_by_degree

