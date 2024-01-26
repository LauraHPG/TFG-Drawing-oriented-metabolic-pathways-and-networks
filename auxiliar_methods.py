import networkx as nx
import sys

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

    return [node for node, data in graph.nodes(data=True) if data['node_type'] == 'reaction'], [node for node, data in graph.nodes(data=True) if data['node_type'] == 'component']

def edges_cross_1D(r1,r2,c1,c2):
    return (r1 < r2 and c1 > c2) or (r2 < r1 and c2 > c1)

def edges_cross_1D_2(r1,r2,c1,c2, c_y1, c_y2, r_y1, r_y2):
    return r_y1 == r_y2 and c_y1 == c_y2 and ((r1 < r2 and c1 > c2) or (r2 < r1 and c2 > c1))

def are_not_coincident(r1, r2, c1, c2):
    return (r1 != r2) and (r1 != c1) and (r1 != c2) and (r2 != c1) and (r2 != c2) and (c1 != c2)

def edges_cross_2D(r1,r2,c1,c2):

    d_e1_e2_1 = determinant(r1[0],r1[1],c1[0],c1[1],r2[0],r2[1])
    d_e1_e2_2 = determinant(r1[0],r1[1],c1[0],c1[1],c2[0],c2[1])

    d_e2_e1_1 = determinant(r2[0],r2[1],c2[0],c2[1],r1[0],r1[1])
    d_e2_e1_2 = determinant(r2[0],r2[1],c2[0],c2[1],c1[0],c1[1])


    return d_e1_e2_1*d_e1_e2_2 < 0 and d_e2_e1_1*d_e2_e1_2 < 0

def determinant(px,py,qx,qy,rx,ry):
	return ((qx-px)*(ry-py) - (rx-px)*(qy-py))

def count_edge_crossings(graph, positions, reactions):
    crosses = 0
    num_crosses_edge = {}
    edge_crossing_edges = {}
    for edge1 in graph.edges():
        num_crosses_edge[edge1] = 0
        edge_crossing_edges[edge1] = set()
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
                
                if edges_cross_1D_2(r1_pos[0],r2_pos[0],c1_pos[0],c2_pos[0], c1_pos[1],c2_pos[1], r1_pos[1], r2_pos[1]):
                # if edges_cross_1D(r1_pos,r2_pos,c1_pos,c2_pos) and are_not_coincident(r1_pos, r2_pos, c1_pos, c2_pos): 
                #     print(f"Nodes: {node1} {node2} {node3} {node4}")
                    crosses += 1
                    num_crosses_edge[edge1] += 1
                    edge_crossing_edges[edge1].add(edge2)
                    
    return crosses // 2, dict(sorted(edge_crossing_edges.items(), key=lambda item: len(item[1]), reverse=True))

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

def get_source_and_sink_nodes(graph):
    nodes = graph.nodes()
    in_degree_list = [(node, degree) for node, degree in graph.in_degree(nodes)]
    out_degree_list = [(node, degree) for node, degree in graph.out_degree(nodes)]
    sink_nodes, source_nodes = [], []
    for in_deg, out_deg in  zip(in_degree_list, out_degree_list):
        if in_deg[0] == out_deg[0]:
            if in_deg[1] == 0: #source
                source_nodes.append(in_deg[0])
            if out_deg[1] == 0: #source
                sink_nodes.append(in_deg[0])


    return source_nodes, sink_nodes

def split_components_1(graph, pos, components):
    new_pos = pos.copy()

    for node in graph.nodes():
        if graph.degree(node) <= 3 and node in components:
            new_pos[node] = (pos[node][0], 3)

    return new_pos

def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def split_reactions_1(graph, pos, reactions):    
    new_pos = pos.copy()

    for node in graph.nodes():
        if node in reactions:
            # adjacent_nodes_iterator = graph.neighbors(node)
            # adjacent_nodes = list(adjacent_nodes_iterator)
            in_nodes = flatten_list(list(graph.predecessors(node)))
            out_nodes = flatten_list(list(graph.successors(node)))

            adjacent_nodes = in_nodes + out_nodes

            first_node = adjacent_nodes[0]

            all_in_one_side = True

            for adjacent_node in adjacent_nodes:
                if not pos[first_node][1] == pos[adjacent_node][1]:
                    all_in_one_side = False
                    break

            if all_in_one_side:
                if pos[node][1] < pos[first_node][1]:
                    new_pos[node] = (pos[node][0], pos[first_node][1] + 2)
                else:
                    new_pos[node] = (pos[node][0], pos[first_node][1] - 2)

    return new_pos

def add_element_to_set(positions, key, element):
    if key not in positions:
        positions[key] = set()
    positions[key].add(element)

def computeStep(size_small, size_big):
    return size_big/size_small

def rearange_positions(positions):
    new_positions = positions.copy()
    nodes_per_y = {}

    for pos in positions:
        add_element_to_set(nodes_per_y,positions[pos][1],pos)
    
    max_size = max(nodes_per_y, key=lambda key: len(nodes_per_y[key]))
    
    for y in nodes_per_y:
        x = 0
        step = computeStep(len(nodes_per_y[y]), max_size)
        for node in nodes_per_y[y]:         
            new_positions[node] = (x,y)
            x += step

    return new_positions

def splitNodes(G, components, reactions, pos):

    doSplit = input("Do you want to split the components? (Y/n)")
    if doSplit == "Y" or doSplit == "y":
        pos = split_components_1(G,pos,components)
        n_crossings, _ = count_edge_crossings(G, pos, reactions)

        print(f"Number of crossings split components: {n_crossings}")

        # subax3 = plt.subplot(132)
        # nx.draw(G, pos, node_color=colors)

        pos = split_reactions_1(G,pos,reactions)
        n_crossings, _ = count_edge_crossings(G, pos, reactions)

        print(f"Number of crossings split reactions: {n_crossings}")
    return pos